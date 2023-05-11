# Auto-Start EC2 Instances on Monday

This Cloud Custodian policy automatically starts EC2 instances starts at the start of week on Monday that meet certain filter criteria. The policy also sends email notifications when instances are stopped.

## 1. Prerequisites

- AWS STS endpoints should be enabled.

- An SQS queue should be created and recipient email addresses should be verified in SES.

- The role used in the policy should have relevant permissions required by the lambda function to start EC2 instances.

- Make sure you are using the LTS version of Cloud Custodian.

- A trail is required to store the CloudTrail events to S3 or CloudWatch.

## 2. Deployment

To deploy this policy, you need to run the following command:

```bash
c7n-mailer --config mailer.yml --update-lambda && custodian run -s output/ startinstance.yml
```

When running this Cloud Custodian policy, the following resources are created:

- A Custodian Lambda function that is responsible for starting EC2 instances that match the filter criteria.

- An Event Bridge Rule is also created to trigger the Lambda function on a schedule.

- In addition, a Lambda function for the Custodian Mailer is created. This function is used to send email notifications based on the actions taken by the auto start policy.

Overall, these resources work together to automatically start EC2 instances and provide notification to the relevant parties about the actions taken by the policy.
![custodianarchi drawio](https://user-images.githubusercontent.com/122358742/222403598-40b557da-5086-4686-b48a-72cdae724a6a.png)

## 3. Explanation

![Wholearchitecturestartinstancestart drawio](https://user-images.githubusercontent.com/122358742/222975313-2ba6d054-7063-4509-8498-c118c1b840e2.png)
This policy starts an EC2 instance on the start of weekdays. The instance must have a tag "onhour" with the boolean value `True` and be in the `stopped` state.

The policy is implemented as a Cloud Custodian policy with the resource type of EC2. It runs in periodic mode on a schedule defined by a CRON expression.

The policy contains several filters to select the appropriate EC2 instances, including checking the state of the instance, the presence of a specific tag, and the time of day.

The actions section of the policy includes two actions: mark-for-op and notify. The mark-for-op action sets a tag on the instance to indicate that it should be started after one day. The notify action sends an email notification to a specified recipient when the instance is stopped. The email notification uses an `HTML` template defined in a `Jinja2` template file.

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
