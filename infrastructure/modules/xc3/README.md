# Terraform XC3 Module

The Terraform XC3 Module is used to create the required infrastructure of XC3. It includes the creation of EC2 insatances, IAM role that will be associated with EC2 instance, EC2 key pair, IAM instance profile, SNS topic, SQS queue, SES email identity, S3 bucket and lambda layer.
The module also allows the user to define custom tags and namespace for the resources created.

### Usage

The XC3 Module can be used by calling the module block and passing the required input variables in `main.tf`, as shown below:


```
module "xc3" {
  source = "./modules/xc3"
  sqs_queue = "notification-queue"
  ses_email_address = "admin@example.co"
  vpc_id            = "vpc-0123456789abcdef0"
  public_subnet_IDs  = ["subnet-0123456789abcdef0"]
  subnet_id = "subnet-0123456789abcdef1"
  namespace                 = "myproject"
  tags = {
    "Project" = "example"
    "Owner"       = "JohnDoe@example.co"
  }
}

```

### Input Variables

| Variable Name      | Description                                                                  | Type          | Default | Required |
| ------------------ | ---------------------------------------------------------------------------- | ------------- | ------- | -------- |
| vpc_id             | The ID of the VPC.                                                           | `string`      | n/a     | Yes      |
| subnet_id          | The ID of the private subnet where EC2 will be created.                      | `string`      | n/a     | Yes      |
| security_group_IDs | The security group IDs that will be associated with EC2 instances.           | `map(string)` | n/a     | Yes      |
| public_subnet_IDs  | The list of public subnet IDs where the load balancer will be created.       | `map(string)` | n/a     | Yes      |
| instance_type      | The EC2 instance type.                                                       | `string`      | n/a     | Yes      |
| ses_email_address  | The email address for SES identity.                                          | `string`      | n/a     | Yes      |
| prometheus_layer   | The S3 key for prometheus layer used to store layer package.                 | `string`      | n/a     | Yes      |
| domain_name        | The domain name for grafana dashboard.                                       | `string`      | n/a     | No       |
| hosted_zone_id     | The public Route 53 hosted zone ID.                                          | `string`      | n/a     | No       |
| namespace          | The namespace to use for the resources created.                              | `string`      | n/a     | Yes      |
| tags               | A map of custom tags to apply to the resources created.                      | `map(string)` | n/a     | Yes      |

### Output Variables

| Variable Name        | Description                                                       |
| -------------------- | ----------------------------------------------------------------- |
| s3_xc3_bucket        | The S3 bucket to be used in lambda functions.                     |
| sns_topic_arn        | The SNS topic arn to be used in lambda functions.                 |
| prometheus_layer_arn | The lambda layer arn to be used in lambda functions.              |
| private_ip           | The private IP of EC2 instance where pushgateway is installed.    |
| xc3_url              | The DNS of the loadbalancer to access dashboard if domain is null |

### Resources Created

- aws_instance: Private EC2 instances in private subnet, where cloud custodian installed

- aws_iam_role: The IAM role that will be associated with EC2 instance.

- aws_ses_email_identity: The SES email identity to be verified for alerting in cloud custodian.

- aws_sqs_queue: The SQS queue to poll messages for alerting and notification.

- aws_sns_topic: The SNS topic for subscription of messages from lambda function.

- aws_s3_bucket: The S3 bucket for artifacts.

- aws_lambda_layer_version: The lambda layer for prometheus client that will be used in lambda functions.

- aws_lb: The AWS loadbalancer that will be used to route traffic to private EC2 instance where grafana/prometheus installed.

- aws_cognito_user_pool: The AWS Cognito user pool that will be used for user access management using OAuth on grafna.

- aws_route53_record: A recod in any existing public hosted zone.


### Dependencies

This module depends on the following provider:

- aws: The official AWS provider for Terraform.
- null: The official null provider for Terraform.

### Limitations

The module currently creating two EC2 instances.
The module does not include versioning on S3 bucket.

### License

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


