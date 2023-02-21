# Cloud Custodian Policy: Auto-tag newly created EC2 instances with owner tag

This policy automatically tags any newly created EC2 instances with the owner tag if it is missing. The value of the owner tag will be the name of the IAM user who created the EC2 instance.

## 1. Prerequisites

- AWS STS endpoints should be enabled.
- An SQS queue should be created and recipient email addresses should be verified in SES.
- The role used in the policy should have relevant permissions required by the lambda function to tag the newly created EC2 resources.
- Make sure you are using the LTS version of Cloud Custodian.
- A trail is required to store the CloudTrail events to S3 or CloudWatch.

## 2. Deployment

To deploy this policy, you need to run the following command:

```bash
c7n-mailer --config mailer.yml --update-lambda && custodian run -s auto-tag-user auto-tag-user.yml
```

When running an auto-tagging Cloud Custodian policy, the following resources are created:

- A Custodian Lambda function that is responsible for tagging newly created EC2 instances with the appropriate tags.

- An Event Bridge Rule is also created to trigger the Lambda function whenever a RunInstances event occurs.

- In addition, a Lambda function for the Custodian Mailer is created. This function is used to send email notifications based on the actions taken by the auto-tagging policy.

Overall, these resources work together to enable automatic tagging of newly created EC2 instances and provide notification to the relevant parties about the actions taken by the policy.

![image](https://user-images.githubusercontent.com/95742163/220266961-6835223a-7b5a-472c-b54b-8d800d7d13d1.png)

## 3. Explanation

### 3.1 Custodian Auto Tagger

---

This policy uses the ec2 resource type to select EC2 instances. The mode is set to cloudtrail and the events list includes only the `RunInstances` event. This means that the policy will only apply to EC2 instances launched by the `RunInstances` API operation.

The filters section checks if the owner tag is absent. If the tag is absent, the actions section adds the owner tag to the instance with the value of the IAM user who created the instance.

The `mailer.yml` configuration file is used by the c7n-mailer tool to send email notifications when the policy is triggered. The `queue_url` value should be replaced with the URL of your own Amazon SQS queue.

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
