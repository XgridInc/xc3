# Cloud Custodian Policy: Auto-tag newly created EKS Clusters with owner tag

This policy automatically tags any newly created EKS clusters with the owner tag if it is missing. The value of the owner tag will be the name of the IAM user who created the EKS cluster.

## 1. Prerequisites

- AWS STS endpoints should be enabled.
- An SQS queue should be created and recipient email addresses should be verified in SES.
- The role used in the policy should have relevant permissions required by the lambda function to tag the newly created EKS resources.
- Make sure you are using the LTS version of Cloud Custodian.
- A trail is required to store the CloudTrail events to S3 or CloudWatch.

## 2. Deployment

To deploy this policy, you need to run the following command:

```bash
custodian run -s auto-tag-user eks-auto-tag-user.yml
```

When running an auto-tagging Cloud Custodian policy, the following resources are created:

- A Custodian Lambda function that is responsible for tagging newly created EKS clusters with the appropriate tags.

- An Event Bridge Rule is also created to trigger the Lambda function whenever a CreateCluster event occurs.

- In addition, a Lambda function for the Custodian Mailer is created. This function is used to send email notifications based on the actions taken by the auto-tagging policy.

Overall, these resources work together to enable automatic tagging of newly created EKS clusters and provide notification to the relevant parties about the actions taken by the policy.

## 3. Explanation

### 3.1 Custodian Auto Tagger

---

This policy uses the eks resource type to select EKS clusters. The mode is set to cloudtrail and the events list includes only the `CreateCluster` event. This means that the policy will only apply to EKS clusters created by the `CreateCluster` API operation.

The filters section checks if the owner tag is absent. If the tag is absent, the actions section adds the owner tag to the EKS cluster with the value of the IAM user who created the cluster.

### 3.2 Custodian Mailer

---

![Image](https://user-images.githubusercontent.com/95742163/219685736-00483f6b-28a2-4f4b-b176-55cfda2e84f4.png)

Here's how the c7n mailer works with SQS and SES:

- The Cloud Custodian policy engine evaluates policies that have been defined in a rules file, and takes the appropriate action(s) based on the evaluation.

- If the policy action is to send an email notification, the c7n mailer is triggered.

- The c7n mailer sends a message to an SQS queue with the details of the email that needs to be sent, including the recipient email addresses, subject, and body of the email.

- A Lambda function is configured to listen to the SQS queue. When a message is received, the Lambda function retrieves the details of the email that needs to be sent.

- The Lambda function uses SES to send the email. It uses the recipient email addresses, subject, and body of the email that were included in the message from the SQS queue.

- SES delivers the email to the recipients.


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
