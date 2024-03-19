import boto3

# import json
# from datetime import datetime, timedelta
import csv
from io import StringIO, BytesIO
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import gzip
import os


def lambda_handler(event, context):
    iam_roles = list_iam_roles()
    role_function_mapping = map_roles_to_lambda_functions(iam_roles)

    bucket_name = os.environ["cur_bucket_name"]
    file_key = os.environ["cur_file_key"]
    # folder = "report/mycostreport/20240301-20240401/"
    # file_key = folder + "20240315T100631Z/mycostreport-00001.csv.gz"
    cost_data = generate_cost_data(role_function_mapping, bucket_name, file_key)
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps(cost_data)
    # }
    # with open('new_cost_data_lambda.json', 'w') as outfile:
    #     json.dump(cost_data, outfile, indent=4)
    print(cost_data)
    # data = cost_data
    # # Aggregate the data by function name
    # aggregated_data = {}
    # for item in data:
    #     function_name = item['FunctionName']
    #     if function_name not in aggregated_data:
    #         aggregated_data[function_name] = []

    #     for result in item['CostData']['ResultsByTime']:
    #         start_date = result['TimePeriod']['Start']
    #         amount = result['Total']['UnblendedCost']['Amount']
    #         aggregated_data[function_name].append
    #          ({'Start': start_date, 'Amount': amount})

    # # Example of the aggregated data structure
    # for function_name, costs in aggregated_data.items():
    #     print(f"Function Name: {function_name}")
    #     for cost in costs:
    #         print(f"Start Date: {cost['Start']}, Amount: {cost['Amount']}")
    #     print("\n")
    # #print(aggregated_data)

    registry = CollectorRegistry()

    # Define the metric
    cost_gauge = Gauge(
        "aws_lambda_function_cost",
        "AWS Lambda function cost",
        ["role_name", "function_name", "start_date"],
        registry=registry,
    )

    # # Populate the metric with data from aggregated_data
    # for function_name, costs in aggregated_data.items():
    #     for cost_info in costs:
    #         cost_gauge.labels(function_name=function_name,
    # start_date=cost_info['Start']).set(float(cost_info['Amount']))

    # Iterate over the original cost_data to populate the metric
    for role_name, role_data in cost_data.items():
        for function_name, costs in role_data["Functions"].items():
            for cost_entry in costs:
                # Populate the Gauge with labels for role,
                # function, and start date, and set the cost as the value
                cost_gauge.labels(
                    role_name=role_name,
                    function_name=function_name,
                    start_date=cost_entry["StartDate"],
                ).set(cost_entry["Cost"])

    # Push the metrics to the Pushgateway
    push_to_gateway(
        os.environ["prometheus_ip"], job="aws_lambda_costs", registry=registry
    )

    print("Data successfully pushed to Prometheus Pushgateway.")


def list_iam_roles():
    iam_client = boto3.client("iam")
    iam_roles = []
    paginator = iam_client.get_paginator("list_roles")
    for page in paginator.paginate():
        for role in page["Roles"]:
            iam_roles.append(role)
    return iam_roles


def map_roles_to_lambda_functions(iam_roles):
    lambda_client = boto3.client("lambda")
    role_function_mapping = []
    paginator = lambda_client.get_paginator("list_functions")
    for page in paginator.paginate():
        for function in page["Functions"]:
            for role in iam_roles:
                if function["Role"] == role["Arn"]:
                    role_function_mapping.append(
                        {
                            "RoleName": role["RoleName"],
                            "RoleArn": role["Arn"],
                            "FunctionName": function["FunctionName"],
                        }
                    )
    return role_function_mapping


def generate_cost_data(role_function_mapping, bucket_name, file_key):
    csv_content = download_and_decompress_csv(bucket_name, file_key)
    csv_reader = csv.DictReader(StringIO(csv_content))

    # Initialize a dictionary to hold cost data for each role
    role_cost_data = {
        mapping["RoleName"]: {"TotalCost": 0, "Functions": {}}
        for mapping in role_function_mapping
    }

    for row in csv_reader:
        if row["lineItem/ProductCode"] == "AWSLambda":
            function_arn = row["lineItem/ResourceId"]
            cost = float(row["lineItem/UnblendedCost"])
            start_date = row["lineItem/UsageStartDate"]

            # Find the corresponding role for the function ARN
            for mapping in role_function_mapping:
                if (
                    mapping["FunctionName"] in function_arn
                ):  # Assuming FunctionName holds the ARN or part of it
                    role_name = mapping["RoleName"]
                    function_name = mapping["FunctionName"]

                    # Initialize function data if not present
                    if function_name not in role_cost_data[role_name]["Functions"]:
                        role_cost_data[role_name]["Functions"][function_name] = {}

                    # Aggregate cost by start date
                    if (
                        start_date
                        in role_cost_data[role_name]["Functions"][function_name]
                    ):
                        role_cost_data[role_name]["Functions"][function_name][
                            start_date
                        ] += cost
                    else:
                        role_cost_data[role_name]["Functions"][function_name][
                            start_date
                        ] = cost

                    # Update the total cost for the role
                    role_cost_data[role_name]["TotalCost"] += cost
                    break

    # Sort the function cost data by date and format it into a list
    for role, data in role_cost_data.items():
        for function_name, date_cost_map in data["Functions"].items():
            sorted_cost_data = [
                {"StartDate": date, "Cost": cost}
                for date, cost in sorted(date_cost_map.items())
            ]
            data["Functions"][function_name] = sorted_cost_data

    return role_cost_data


def download_and_decompress_csv(bucket_name, file_key):
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    # Decompose the file content
    with gzip.GzipFile(fileobj=BytesIO(response["Body"].read())) as gz:
        file_content = gz.read().decode("utf-8")

    return file_content


# lambda_handler(1,2)
