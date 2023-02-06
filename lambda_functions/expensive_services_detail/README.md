# Overview

This lambda function uses the AWS Cost Explorer API to find the 5 most expensive services in a provided AWS region over the last 14 days. This code is intended to be used as an AWS Lambda function, and it uses the Prometheus client library to push the data to a Prometheus Push Gateway.

The script imports several libraries at the top, including json, boto3, os,  logging, date, timedelta, and prometheus_client.

# Working

The script starts by initializing the runtime_region variable with the value of the AWS_REGION environment variable. Then, it creates a boto3 client for the Cost Explorer API.

The script defines a lambda_handler function that takes two arguments: event, and context. It uses the context variable to get the AWS account ID. Then, it defines two variables start and end to represent the start and end date for the 14 days.

Then, it uses the Cost Explorer API to get the cost and usage data for the specified time period, filtering by the SERVICE dimension. It sorts the services by their costs and takes the first 5 services.

It then uses the Prometheus client library to create a gauge for the data, setting the labels for the gauge with the service name, cost, region, and account ID. Finally, it pushes the gauge data to a Prometheus Push Gateway, defined by the prometheus_ip environment variable. The function returns a JSON response indicating whether the metrics were pushed successfully or not.