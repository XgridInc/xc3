# Auto-Stop EC2 Instances on Weekends

This Cloud Custodian policy automatically stops EC2 instances on weekends that meet certain filter criteria. The policy also sends email notifications when instances are running.

## 1. Prerequisites

- AWS STS endpoints should be enabled.

- An SQS queue should be created and recipient email addresses should be verified in SES.

- The role used in the policy should have relevant permissions required by the lambda function to stop EC2 instances.

- Make sure you are using the LTS version of Cloud Custodian.

- A trail is required to store the CloudTrail events to S3 or CloudWatch.

## 2. Deployment

To deploy this policy, you need to run the following command:

```bash
c7n-mailer --config mailer.yml --update-lambda && custodian run -s output/ stopinstance.yml
```

When running this Cloud Custodian policy, the following resources are created:

- A Custodian Lambda function that is responsible for stopping EC2 instances that match the filter criteria.

- An Event Bridge Rule is also created to trigger the Lambda function on a schedule.

- In addition, a Lambda function for the Custodian Mailer is created. This function is used to send email notifications based on the actions taken by the auto stop policy.

Overall, these resources work together to automatically stop EC2 instances and provide notification to the relevant parties about the actions taken by the policy.

![custodianarchistopinstance drawio](https://user-images.githubusercontent.com/122358742/222974375-816e78d5-5466-4eff-a895-82a863cf5168.png)

## 3. Explanation

![Wholearchitecturestartinstancestop drawio(1)](https://user-images.githubusercontent.com/122358742/222975243-5d5bf4fc-d68d-46f3-8235-b9fa52bf4c49.png)

This policy stops an EC2 instance at the start of weekends. The instance must have the tag "offhour" with the boolean value `True` and in the `start` state.

The policy is implemented as a Cloud Custodian policy with the resource type of EC2. It runs in periodic mode on a schedule defined by a CRON expression.

The policy contains several filters to select the appropriate EC2 instances, including checking the state of the instance, the presence of a specific tag, and the time of day.

The actions section of the policy includes two actions: mark-for-op and notify. The mark-for-op action sets a tag on the instance to indicate that it should be stopped after one day. The notify action sends an email notification to a specified recipient when the instance is stopped. The email notification uses an HTML template defined in a `Jinja2` template file.

The transport for the email notification is Amazon SQS, with the queue specified in the policy configuration and lastly SES sends an email to the user/group as needed.

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
