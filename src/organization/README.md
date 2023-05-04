# **List Members Accounts**

This Lambda function retrieves a list of all member accounts linked with a master AWS account in AWS Organizations and puts that list in an SSM Parameter.

## **List Linked Accounts Workflow**
![linked-Accounts](https://user-images.githubusercontent.com/114464405/235909127-56b6bdd5-5754-48e8-9199-6e2d634af316.png)

The function is written in Python and uses the Boto3 library to interact with AWS services.

The function takes an event and context as input, and returns a dictionary containing a status code and a JSON-encoded list of account details. The account details include the account ID and account name concatenated with a hyphen.

The Lambda function uses two Boto3 clients, "organizations" and "ssm", to retrieve the list of accounts and put it in an SSM Parameter. The function first initializes an empty list to hold the linked accounts, and then uses the "list_accounts" API to retrieve all accounts under the specified master account. The function then concatenates the account ID and account name for each linked account, and puts the resulting list in an SSM Parameter.

The function handles errors that may occur during the execution, such as network connectivity issues, incorrect account ID, or problems in calling organization APIs or creating an SSM parameter. The function logs errors using the Python logging module.

To use this Lambda function, you can deploy it in your AWS account and create an event trigger for it. You can also set an environment variable "account_detail" to specify the name of the SSM parameter where the account details will be stored. Ensure that the IAM role assigned to the Lambda function has sufficient permissions to access the necessary resources such as Organizations and SSM.

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
