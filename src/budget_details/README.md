# Overview

These lambda function use the AWS Cost Explorer API to find the spend of each project in an AWS account and the total cost of an account in a month. This code is intended to be used as an AWS Lambda function, and it uses the Prometheus client library to push the data to a Prometheus Push Gateway.

The script imports several libraries at the top, including json, boto3, os, logging, date, timedelta, and prometheus_client.

# Working

The script starts by initializing the runtime_region variable with the value of the AWS_REGION environment variable. Then, it creates a boto3 client for the Cost Explorer API.

- **Project Spend Cost**

The script for project_spend_cost defines a lambda_handler function that takes two arguments: event, and context. It uses the context variable to get the AWS account ID. Then, it defines two variables start and end to represent the start and end date for the 30 days.

Then, it uses the Cost Explorer API to get the cost and usage data for the specified time period, filtering by the GroupBy dimension. The dimension uses the TAG filter with Project as its key to get the costs of Projects. Then, it invokes the project cost breakdown lambda function asynchronously passing the project name as payload.

- **Project Cost Breakdown**

The script for project_cost_breakdown defines a lambda_handler function that takes two arguments: event, and context. It uses the event variable to get the Project name and, context variable to get the AWS account ID. Then, it defines two variables start and end to represent the start and end date for the 30 days.

Then, it uses the Cost Explorer API to get the cost and usage data for the specified time period, filtered by the Filter dimension. The dimension uses the TAG filter with Project as its key and Project name as its value to get the costs of specified Project. It uses GroupBy SERVICE dimension to group the response based on service.

- **Total Account Cost**

The script for total_account_cost defines a lambda_handler function that takes two arguments: event, and context. It uses the context variable to get the AWS account ID. Then, it defines two variables start and end to represent the start and end date for the 14 days.

Then, it uses the Cost Explorer API to get the cost and usage data for the specified time period, filtering by the Filter dimension. The dimension uses the LINKED_ACCOUNT filter with account id as input to get the costs of accounts.

- **Pushing the Data for Prometheus**

It then uses the Prometheus client library to create a gauge for the data, setting the labels for the gauge with the the name of project and its cost. Finally, it pushes the gauge data to a Prometheus Push Gateway, defined by the prometheus_ip environment variable. The function returns a JSON response indicating whether the metrics were pushed successfully or not.

## License

Copyright (c) 2023, Xgrid Inc, https://xgrid.co

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
