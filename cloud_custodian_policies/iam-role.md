# Policy: IAM Roles in Use

This policy is designed to ensure that IAM roles in your AWS account are being used. It periodically scans your IAM roles and generates a report of all roles that have not been used for a specified amount of time. You can use this policy to identify and remove unnecessary IAM roles, reducing the risk of unauthorized access and improving the security posture of your AWS account.

## Policy Details

### Name

`iam-roles-in-use`

### Resource

`iam-role`

### Mode

The policy runs in `periodic` mode, which means it will be executed at a fixed interval. The schedule for this policy is set to run at `5:00 AM UTC` every day.

### Role

The policy requires a `role` parameter, which is the ARN of an IAM role with the necessary permissions to execute this policy. This IAM role should have read access to all IAM roles in your AWS account.

### Actions

The policy scans all IAM roles in your AWS account and generates a report of all roles that have not been used for a specified amount of time. The report is sent to the specified SNS topic.

### Results

The policy generates a report of all IAM roles that have not been used for a specified amount of time. The report includes the following information:

- Role name
- Creation date
- Last used date (if available)
- Status (active or inactive)

## How to Use This Policy

To use this policy, you will need to:

1. Create an IAM role with the necessary permissions to execute this policy.
2. Configure the policy with the ARN of the IAM role created in step 1.
3. Optionally, specify the time period after which a role is considered unused.
4. Specify the SNS topic to receive the report.
5. Save and apply the policy.

Once the policy is applied, it will run at the specified schedule and generate a report of all IAM roles that have not been used for the specified amount of time. You can review the report and take appropriate action, such as deleting unnecessary IAM roles or disabling inactive roles.

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
