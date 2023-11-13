# Integration Tests for AWS Infrastructure

This repository contains integration tests designed to validate various aspects of the AWS infrastructure and services used by the application. These tests are written using the AWS SDK for Python (Boto3) and follow best practices for integration testing to ensure the correctness and reliability of the infrastructure.

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Test Cases](#test-cases)
  - [CloudTrail S3 Bucket Configuration](#cloudtrail-s3-bucket-configuration)
  - [CloudWatch Metrics for Most Expensive Service](#cloudwatch-metrics-for-most-expensive-service)
  - [EC2 Instance Configuration](#ec2-instance-configuration)
  - [Lambda Functions Configuration](#lambda-functions-configuration)
  - [Load Balancer Configuration](#load-balancer-configuration)
  - [SNS Topic Subscription](#sns-topic-subscription)
  - [VPC Configuration](#vpc-configuration)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

## Introduction

These integration tests are designed to ensure that the AWS infrastructure and services are correctly configured and working as expected. The tests cover various aspects of the infrastructure, such as CloudTrail configuration, CloudWatch metrics, EC2 instances, Lambda functions, load balancer configuration, SNS topic subscriptions, and VPC configuration.

## Prerequisites

Before running the integration tests, ensure that you have the following prerequisites:

- AWS account credentials with sufficient permissions to interact with the services being tested.
- Python 3.x installed on your system.
- `boto3` library installed. You can install it using the following command:

```sh
pip install boto3
```


## Test Cases

### CloudTrail S3 Bucket Configuration

- Verifies the correctness of CloudTrail S3 bucket configuration.
- Ensures that CloudTrail trails are correctly associated with the specified S3 bucket.
- Uses Boto3 to connect to the CloudTrail service and retrieve trail information.

### CloudWatch Metrics for Most Expensive Service

- Validates CloudWatch metrics for the most expensive service Lambda function.
- Checks if the function name and metrics match the expected values.
- Uses Boto3 to interact with CloudWatch and retrieve metric information.

### EC2 Instance Configuration

- Checks if EC2 instances have the correct VPC and security group configurations.
- Verifies the assigned VPC ID and security group ID for specified instances.
- Uses Boto3 to describe instances and extract configuration details.

### Lambda Functions Configuration

- Validates various aspects of Lambda function configurations.
- Tests VPC configuration, total account cost calculation, and other Lambda functions.
- Invokes Lambda functions and verifies their responses using Boto3.

### Load Balancer Configuration

- Tests load balancer configurations, including VPC and subnet assignments.
- Verifies that the load balancer is associated with the correct VPC and subnets.
- Uses Boto3 to describe load balancers and extract configuration details.

### SNS Topic Subscription

- Checks if the endpoint of an SNS topic subscription matches the specified Lambda function.
- Verifies that the Lambda function ARN matches the SNS topic subscription endpoint.
- Uses Boto3 to describe SNS topic subscriptions and extract endpoint information.

### VPC Configuration

- Validates VPC configuration, including CIDR block and subnet assignments.
- Verifies that the VPC has the correct CIDR block and subnets.
- Uses Boto3 to describe VPCs and subnets and extract configuration details.

## Running Tests

1. Clone this repository to your local machine.
2. Set up your AWS credentials and configure your environment as needed.
3. Navigate to the root directory of the repository.
4. Run the tests using the following command inside the ./tests/integration-testing folder:

```sh
cd ./tests/integration-testing
pytest *.py
```

The tests will be executed, and the results will be displayed in the terminal.

## Contributor

XC3 is a community-driven project; we welcome your contribution! For code contributions, please read our [contribution guide](./CONTRIBUTING.md).

- File a [GitHub issue](https://github.com/XgridInc/xc3/issues) to report a bug or request a feature.
- Join our [Slack](https://join.slack.com/t/xgrid-group/shared_invite/zt-1uhzlrt6t-Dx_BqfQJKsHhSug1arbbAQ) for live conversations and quick questions.

<br clear="all">

## RoadMap

We welcome feedback and suggestions from our community! Please feel free to create an issue or join our discussion forum to share your thoughts.
For project updates, please read our [roadmap guide](./ROADMAP.md).

## License

XC3 is licensed under [Apache License, Version 2.0](./LICENSE).


