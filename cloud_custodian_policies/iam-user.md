# Policy: IAM Users In Use

This policy is designed to identify IAM users that are not in use in your AWS account. It ensures that unused IAM users are disabled or deleted to maintain security and compliance.

## How it works

This policy uses a periodic mode to run daily at 5:00 AM UTC and lists all the IAM users in the AWS account. It then checks whether each user has logged in at least once in the last 90 days. If a user has not logged in for the specified period, the policy takes action to disable or delete the user as configured.

## Policy configuration

To use this policy, you need to set up the following:

- **Resource:** IAM User
- **Mode:** Periodic with a schedule of `cron(0 5 * * ? *)`
- **Role:** A role with the necessary permissions to read and modify IAM users. You can specify the role ARN as `arn:aws:iam::{account_id}:role/onboarding-custodian-role` in the policy.

## Actions

This policy can perform the following actions based on the configuration:

- **Disable user:** Disables the IAM user that has not logged in for the specified period.
- **Delete user:** Deletes the IAM user that has not logged in for the specified period.

## Compliance

This policy helps ensure compliance with the following AWS Security Best Practices:

- [IAM Best Practices: Delete Users or Passwords No Longer in Use](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#delete-unused-credentials)

## Notes

- This policy only looks at the login history of IAM users in the AWS account. It does not consider users that may be authenticated via external identity providers.
- This policy can have significant consequences, especially if it is set to delete IAM users. Please ensure that you test and validate the policy before applying it to production environments.


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
