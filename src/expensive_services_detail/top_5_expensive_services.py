import boto3
import botocore
import os
import zipfile
from io import BytesIO
import pandas as pd
import logging
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import json

# Initialize and Connect to the AWS EC2 Service
try:
    s3 = boto3.client("s3")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))

bucket_name = os.environ["bucket_name_get_report"]
report_prefix = os.environ["report_prefix"]


def get_latest_cost_and_usage_report(bucket_name, report_prefix):
    """
    Gets the latest Cost and Usage Report from an S3 bucket based on the timestamp
    in the object key.
    Parameters:
    - bucket_name (str): The name of the S3 bucket.
    - report_prefix (str): The prefix of the S3 object key where the reports are stored.

    Returns:
    - str: The key of the latest Cost and Usage Report in the S3 bucket.
    """
    # List objects in the S3 bucket with the specified prefix
    response = s3.list_objects(Bucket=bucket_name, Prefix=report_prefix)

    # Extract the keys and timestamps from the response
    report_keys = [
        (obj["Key"], obj["LastModified"]) for obj in response.get("Contents", [])
    ]

    # Sort the keys based on the LastModified timestamp in descending order
    sorted_report_keys = sorted(report_keys, key=lambda x: x[1], reverse=True)
    # Return the key of the latest report
    if sorted_report_keys:
        latest_report_key = sorted_report_keys[0][0]
        return latest_report_key
    else:
        print("No Cost and Usage Reports found.")
        return None


def read_content_of_report():
    latest_report_key = get_latest_cost_and_usage_report(bucket_name, report_prefix)
    response = s3.get_object(Bucket=bucket_name, Key=latest_report_key)
    zipContent = response["Body"].read()
    # Unzip the report in memory
    with zipfile.ZipFile(BytesIO(zipContent), "r") as zip_ref:
        # Assume there's only one file in the zip archive (adjust as needed)
        csv_file_name = zip_ref.namelist()[0]
        print(csv_file_name)
        # Read the CSV file directly into a pandas DataFrame
        df = pd.read_csv(BytesIO(zip_ref.read(csv_file_name)))
    return df


def classify_ec2_category(row):
    """
    Classify the service category for rows with 'Amazon Elastic Compute Cloud'
    based on the 'lineItem/ResourceId'.
    Parameters:
    - row (pd.Series): A row from the DataFrame.

    Returns:
    - str: The service category ('Ec2' or 'Ec2-Others').
    """
    if row["product/ProductName"] == "Amazon Elastic Compute Cloud":
        resource_id = str(row["lineItem/ResourceId"])
        if resource_id.startswith("i-"):
            return "Ec2"
        else:
            return "Ec2-Others"
    else:
        return row["product/ProductName"]


def extract_cost_by_service_and_region(data):
    """
    Extracts the cost of each service in each region from the Cost and Usage Report.

    Parameters:
    - csv_file_path (str): The path to the Cost and Usage Report CSV file.

    Returns:
    - pd.DataFrame: A DataFrame containing the extracted information.
    """

    # Assuming typical column names, adjust these based on your CSV structure
    relevant_columns = [
        "product/region",
        "product/ProductName",
        "lineItem/ResourceId",
        "lineItem/UnblendedCost",
    ]

    # Filter relevant columns
    df = data[relevant_columns]
    # Classify service category for 'Amazon Elastic Compute Cloud'
    df["ServiceCategory"] = df.apply(classify_ec2_category, axis=1)

    # Group by Product (service) and Region, summing the costs
    grouped_df = (
        df.groupby(["product/region", "ServiceCategory"])["lineItem/UnblendedCost"]
        .sum()
        .reset_index()
    )
    # Get the top N most expensive services for each region
    top_services_df = (
        grouped_df.groupby(["product/region"])
        .apply(lambda x: x.nlargest(5, "lineItem/UnblendedCost"))
        .reset_index(drop=True)
    )

    return top_services_df


def create_and_push_gauge(data):
    try:
        # Creating an empty list to store the data
        data_list = []

        # Adding the extracted cost data to the Prometheus
        # gauge as labels for service, region, and cost.
        registry = CollectorRegistry()
        gauge_top_service_cost = Gauge(
            "top_service_cost",
            "Cost of top 5 services by region",
            ["region", "service"],
            registry=registry,
        )
        # Iterate over rows using a for loop
        for index, row in data.iterrows():
            region = row["product/region"]
            service = row["ServiceCategory"]
            cost = row["lineItem/UnblendedCost"]
            gauge_top_service_cost.labels(region=region, service=service).set(
                float(cost)
            )

            # add the dictionary to the list
            data_dict = {"Service": service, "Region": region, "Cost": cost}
            data_list.append(data_dict)

        # Push the metric to the Prometheus Gateway
        push_to_gateway(
            os.environ["prometheus_ip"], job="services_cost", registry=registry
        )
        # convert data to JSON
        json_data = json.dumps(data_list)
        return json_data

    except Exception as e:
        logging.error("Error initializing Prometheus Registry and Gauge: " + str(e))
        return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}


def push_to_s3_bucket(json_data):
    # upload JSON file to S3 bucket
    key_name = (
        f'{os.environ["top5_expensive_service_prefix"]}/top5_expensive_service.json'
    )
    try:
        s3.put_object(Bucket=os.environ["bucket_name"], Key=key_name, Body=json_data)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            raise ValueError(f"Bucket not found: {os.environ['bucket_name']}")
        elif e.response["Error"]["Code"] == "AccessDenied":
            raise ValueError(f"Access denied to S3 bucket: {os.environ['bucket_name']}")
        else:
            raise ValueError(f"Failed to upload data to S3 bucket: {str(e)}")


def lambda_handler(event, context):
    df = read_content_of_report()
    expensiveService = extract_cost_by_service_and_region(df)
    json_data = create_and_push_gauge(expensiveService)
    push_to_s3_bucket(json_data)
    # Return the response
    return {"statusCode": 200, "body": json.dumps(json_data)}
