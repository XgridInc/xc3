# Terraform Serverless Module

The Terraform serverless Module is used to create the required lambda functions of XC3. It includes the creation of lambda functions, IAM role that will be associated with lambda functions, cloud watch events, lambda permissions, cloud wathc event policy, S3 bucket notification and SNS topic subscription.
The module also allows the user to define custom tags and namespace for the resources created.

### Usage
The Serverless Module can be used by calling the module block and passing the required input variables in `main.tf`, as shown below:

```
module "serverless" {
  source = "./modules/serverless"
  memory_size = 128
  timeout = 300
  s3_xc3_bucket = "example_bucket"
  security_group_id            = "sg-0123456789a"
  subnet_id = "subnet-0123456789abcdef1"
  namespace                 = "myproject"
  tags = {
    "Project" = "example"
    "Owner"       = "JohnDoe@example.co"
  }
}
```

### Input Variables

| Variable name       | Description                                               | Type     | Default | Required |
| ------------------- | --------------------------------------------------------- | -------- | ------- | -------- |
| prometheus_ip       | The private IP of the EC2 instance where Prometheus is installed. | `string` | `null`  | Yes      |
| subnet_ID           | The ID of the private subnet where the Lambda functions will be created. | `string` | `null`  | Yes      |
| security_group_ID   | The security group ID that will be associated with the Lambda functions. | `string` | `null`  | Yes      |
| prometheus_layer    | The ARN of the Prometheus layer.                           | `string` | `null`  | Yes      |
| sns_topic_arn       | The ARN of the SNS topic.                                  | `string` | `null`  | Yes      |
| s3_xc3_bucket       | The S3 bucket ID.                                          | `string` | `null`  | Yes      |
| memory_size         | The amount of memory to allocate to the Lambda function.   | `number` | `null`  | Yes      |
| timeout             | The number of seconds before the Lambda function times out.| `number` | `null`  | Yes      |
| namespace           | The namespace to use for the resources created.           | `string` | `null`  | Yes      |
| tags                | A map of custom tags to apply to the resources created.    | `map`   | `null`  | Yes      |


### Resources Created

- aws_lambda_function: The lambda functions will be created for XC3 workflows i.e total_account_cost, project_spend_cost, most_expensive_service, iam_user_workflow, iam_role_workflow. The function code will be packaged and uploaded to S3.

- aws_iam_role: The IAM role that will be associated with the lambda functions. The role will have the necessary permissions to execute the lambda functions.

- terraform_data: The terraform_data resource to remove zip files created for lambda packages.

- aws_cloudwatch_event_rule: The cloudwatch event rule that will be attach with lambda functions. This rule will trigger the lambda functions based on a schedule or an event.


- aws_cloudwatch_event_rule: The cloudwatch event rule that will be attach with lambda functions.


### Dependencies

This module depends on the following provider:

- aws: The official AWS provider for Terraform.
- null: The official null provider for Terraform.
- archive: The official archive provider for Terraform.

### Limitations

The module does not include encryption on evironment variables in lambda functions as well as tracing.

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
