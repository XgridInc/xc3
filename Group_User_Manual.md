# Contents
[1 Introduction	4](#_toc143538384)

[1.1 Overview	4](#_toc143538385)

[1.2 Purpose	5](#_toc143538386)

[1.3 Scope	5](#_toc143538387)

[1.4 Intended Audience	5](#_toc143538388)

[1.5 Architecture of Implementation	6](#_toc143538389)

[1.6 Warning	7](#_toc143538390)

[2 Getting Started	8](#_toc143538391)

[2.1 Cautions and Warnings	11](#_toc143538392)

[2.2 Set-up Considerations	11](#_toc143538393)

[2.3 User Access Considerations	11](#_toc143538394)

[2.4 Accessing the System	11](#_toc143538395)

[2.5 System Organization and Navigation	11](#_toc143538396)

[2.6 Exiting the System	11](#_toc143538397)

[2.7 Summary of Usage	12](#_toc143538398)

[3. Notification Services	13](#_toc143538399)

[3.1 Total Account Cost Notifications	13](#_toc143538400)

[3.2 Resource Cost Notifications	15](#_toc143538401)

[3.3 IAM User Notifications	18](#_toc143538402)

[3.4 Cronjob	19](#_toc143538403)

[3.5 Cloudwatch Integration	21](#_toc143538404)

[4 Integration	23](#_toc143538405)

[4.1 Integrating python and terraform files	23](#_toc143538406)

[4.2 Implementing Global Variables	23](#_toc143538407)

[5. Troubleshooting	28](#_toc143538408)

[5.1 Common Issues and Solutions	28](#_toc143538409)

[5.1.1 Email Not Being Sent	28](#_toc143538410)

[5.1.2 Slack Message Not Being	28](#_toc143538411)

[5.1.3 Bucket Access Denied	28](#_toc143538412)

[5.1.4 Usage Access Denied	28](#_toc143538413)

[5.1.5 Error Messages	29](#_toc143538414)

[5.1.6 Issues with Terraform	29](#_toc143538415)

[5.2 FAQs	31](#_toc143538416)

[6. Appendices	34](#_toc143538417)

[6.1 Sample Screenshots	34](#_toc143538418)

[Example of Email	34](#_toc143538419)

[Example of Slack Message	35](#_toc143538420)

[6.2 Code Snippets	35](#_toc143538421)

[Code for Email	35](#_toc143538422)

[Code for Slack	36](#_toc143538423)

[Code for Pushing metrics to Cloudwatch	37](#_toc143538424)

[Before/After files Integration	38](#_toc143538425)

[Before/After terraform file	39](#_toc143538426)

[Before/After python file	39](#_toc143538427)





# <a name="_toc143023214"></a><a name="_toc143538384"></a>1 Introduction

## <a name="_toc143538385"></a>1.1 Overview
XC3 is a cloud monitoring tool developed by XGrid. It is a open source tool that aim to make Cloud monitoring easier, more efficient, and cost-effective. It is designed to help businesses achieve operational efficiency in their cloud infrastructure while effectively managing and controlling cloud costs.

In today's cloud-centric landscape, managing cloud costs has become a critical aspect of successful operations. XC3 addresses the challenges businesses face in controlling cloud costs and provides a comprehensive set of features to streamline cost optimization strategies.

XC3 leverages the power of open-source tools such as Cloud Custodian, Prometheus, and Grafana to provide a robust and scalable solution for cloud cost control. Cloud Custodian helps enforce policies and governance across multiple cloud platforms, while Prometheus collects and stores metrics data for monitoring. Grafana offers interactive dashboards and visualization capabilities.

The open-source nature of XC3 invites contributions from the community. Users are encouraged to report issues and suggest enhancements to make XC3 a go-to solution for cloud cost control.

**Why XC3**: Controlling cloud costs presents several challenges, including complexity in cost attribution, identifying expensive resources, managing unused or underutilized resources, lack of visibility into cloud usage, and a lack of expertise in cloud cost management.

XC3 addresses these challenges by providing a comprehensive solution. It offers real-time visibility into cloud usage and costs, enabling businesses to optimize resource utilization, track spending across multiple providers and accounts, and achieve cost savings and efficiency.

By implementing XC3, businesses can reduce unnecessary cloud costs, prevent overspending, and maximize the value of their cloud investments. It empowers organizations with the tools and insights needed to effectively control and manage their cloud infrastructure costs.

In summary, XC3 is an open-source cloud cost control solution that offers features like cost monitoring, idle resource detection, custom alerts, and more. It helps businesses overcome the challenges associated with cloud cost management and enables them to achieve operational efficiency and cost optimization in their cloud infrastructure.

We have attempted to contribute to the development of XC3 by working on its alerting feature. It will notify users who can set their own message channels and budgets. Our implementation works on 3 routes: total account cost, IAM user cost, and services cost. Our implementation of this is already integrated into XC3 and doesn’t interfere with its working at all. By simply having our files, with its additional variables, the notification feature works completely with XC3. Thos document is the user manual of our implementation

## <a name="_toc143023215"></a><a name="_toc143538386"></a>1.2 Purpose
This use manual provides a comprehensive guidance on the implementation and usage of our teams implementation of the Notification Services feature in the XC3 Cloud Monitoring Services. It will also discuss our integration of features that now work within XC3 without any further modification. 
## <a name="_toc143538387"></a>1.3 Scope
This manual covers the setup, configuration, documentation, and utilization of the Notification Services feature. The scope of this manual is to cover the works of the entire team to the XC3 project. This document will break down the parts as implemented and discuss the overall implementation and how its integrated into the existing XC3 product.
## <a name="_toc143023217"></a><a name="_toc143538388"></a>1.4 <a name="_toc143028440"></a>Intended Audience
This User Manual is designed for technical team members, our instructor, and developers who are engaged with the XC3 project. The manual assumes a foundational understanding of cloud technologies, AWS services, Git Version Control, and infrastructure deployment using Terraform. It serves as a valuable resource for those seeking insights into the design, implementation, and integration of budget-based alerts for cost monitoring and reporting in XC3. 
## <a name="_toc143538389"></a>1.5 Architecture of Implementation
![A screenshot of a computer

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.002.png)

*Figure 1: Our Architecture*

As seen above, our architecture involves our 3 primary lambdas that work independently for 3 notification services. They are individually triggered by their own Cronjobs, send metrics to Cloudwatch for monitoring, uses SES and Slack API to alert users, and uses S3 bucket for retrieving metrics.

This is its place in the overall architecture of XC3 as seen below:

![A screenshot of a computer

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.003.png)

*Figure 2: Our Architecture within XC3*

## <a name="_toc143023218"></a><a name="_toc143538390"></a>1.6 Warning
In order to use XC3 and its alerting feature, Amazon Web Services account ID needs to be provided. Security keys are also required. XC3 and our alerting features are launched through that account. Disclosure of that account ID can put users at risk of data leaks, unauthorized access, and use of resources through (and incurring charges) that the owner might not be aware of. When modifying or sharing these files be aware not to share these sensitive data with anyone else


#

# <a name="_toc143028442"></a><a name="_toc143538391"></a>2 Getting Started

This section provides a step-by-step walkthrough of the setup and initiation process for the “Alerting” feature within the XC3 project. The sequence and flow of actions are outlined to guide users through the initial stages up to the successful initiation of the feature. Screen prints with captions are included as well.

**Step 1: Environment Setup**

1. Open your preferred integrated development environment (IDE) such as Visual Studio Code.
1. Ensure that the required extensions and dependencies are installed for complete resource setup. The requirements are:
- [Terraform](https://www.terraform.io/downloads.html) 1.0+
  - [Python](https://www.python.org/downloads) 3.9
  - [AWScli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
  - [Cloud Custodian](https://cloudcustodian.io/docs/quickstart/index.html#install-cloud-custodian)
  - [Prometheus/Grafana/Pushgateway](https://github.com/Einsteinish/Docker-Compose-Prometheus-and-Grafana.git)
  - [checkov](https://github.com/bridgecrewio/checkov) 2.0.574 or later
  - [shellcheck](https://github.com/koalaman/shellcheck) 0.7.1 or later

**Step 2: Code Configuration**

1. Clone the project fork repository from the version control using Git command:                        git clone <https://github.com/AamodPaud3l/Team1_Alert.git>
1. Navigate into the forked repository locally.

**Step 3: Environment Variables**

1. You will need your slack webhook URL. So, 
   1. go to <https://api.slack.com/> (make sure you are logged in)
   1. Under ‘Your Apps’, select ‘Create New App’
   1. Click ‘From Scratch’. Enter App Name and pick the workspace you want your slack notifications in. 

![A screenshot of a computer

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.004.png)

1. Finally, click ‘Create’.
1. After its created, click on the app. One the left side, under **Features** you will see ‘Incoming Webhooks’. Click it.
1. Activate Incoming Webhooks using the slider on the heading. Scroll down to find your unique webhook URL.![A screenshot of a channel

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.005.png)
1. Go to the directory xc3/ and configure the input.sh file

env="dev"

namespace="example"

project="example"

region="ap-southeast-2" # Based on region you want to work on  

allow\_traffic="0.0.0.0/0"

domain="" #  [Optional] - If you want to use your own domain then set this variable.

account\_id="123456789012"

hosted\_zone\_id="Z053166920YP1STI0EK5X"

owner\_email="admin@example.co"

creator\_email="admin@example.co"

ses\_email\_address="admin@example.co"

bucket\_name="example"

slack\_url= “Your unique URL” # Paste your slack webhook URL

1. Also, go to xc3/infrastructure and update the terraform.auto.tfvars file with your custom values:

slack\_channel\_url="Your webhook URL"

budget\_amount = 25

services\_budget\_amount = 5

iam\_budget\_amount = 2

bucket\_name = "example-metadata-storage"

**Step 4:** **Deploying the infrastructure**

1. In the xc3/ directory, perform:   bash init.sh

You will receive a prompt asking ‘Do you want to create a separate IAM role?’. Enter ‘n’. After that, it will deploy the entire architecture with the alerting lambda functions. You will also receive an email asking for verification, click on the link in the email to verify to receive email for alerts. 

Also, since dummy data is being used for total\_cost\_by\_service and total\_cost\_by\_iam\_user, make sure to upload the dummy json files into the S3 metadata storage manually.

For testing purposes, the cronjobs have been set to send message every fifteen after deployment. However, that can be changed under cd/infrastructure/variables.tf file where variable “cron\_job\_schedule” is defined with default values.

variable "cron\_jobs\_schedule" {

`  `description = "Cron job schedule"

`  `type        = map(string)

`  `default = {

`    `resource\_list\_function\_cron   = "cron(0 0 \* \* ? 1)"

`    `list\_linked\_accounts\_cron     = "cron(0 0 1 \* ? \*)"

`    `most\_expensive\_service\_cron   = "cron(0 0 \* \* ? 1)"

`    `cost\_report\_notifier\_cronjob  = "cron(0 0 1,15 \* ? \*)"

`    `total\_cost\_by\_service\_cronjob = "cron(0/15 \* \* \* ? \*)"

`    `iam\_user\_cost\_cronjob         = "cron(0/15 \* \* \* ? \*)" 

`  `}

}

After the deployment, it will show a message in the termal “XC3 Deployment Done!”. Now, you can see the lambda functions from the account. Also, the cloudwatch metrics that get updated every 15 minutes (by default) can be seen.
## <a name="_toc143028443"></a><a name="_toc143538392"></a>2.1 Cautions and Warnings
**Cautions**: It's important to note that the "Alerting" feature involves working with AWS services and sensitive data. Ensure that confidential information, such as access keys and credentials, is not shared within the system or this documentation. Unauthorized access to or sharing of this information can result in security breaches and data leaks.
## <a name="_toc143028444"></a><a name="_toc143538393"></a>2.2 Set-up Considerations
**Equipment**: To implement the feature, you’ll need a computer or device with a modern web browser and an IDE, internet connectivity, and access to AWS services.

**System Configuration:** The system operates within your AWS environment. No special network configurations are required, but access to the AWS Management Console is necessary. Also, AWS needs to be configured in the local environment with private access key ID and secret access key. Finally, make sure ‘CostExplorer’ is enabled in the account.
## <a name="_toc143028445"></a><a name="_toc143538394"></a>2.3 User Access Considerations
**User Roles:** IAM user with necessary permissions is needed for your AWS account, ensuring proper segregation of duties and restricted access as needed. 
## <a name="_toc143028446"></a><a name="_toc143538395"></a>2.4 Accessing the System
To access the system, log in to your AWS account. Your existing credentials will be used to access the functions.
## <a name="_toc143028447"></a><a name="_toc143538396"></a>2.5 System Organization and Navigation
**Organization:** The “Alerting” feature is integrated within the XC3 project environment. The main components include Lambda functions, Cloudwatch, and SES.

**Navigation:** After accessing the AWS account, navigate to the relevant services and functions associated with the “Alerting” feature. For specific instructions, refer to the corresponding sub-sections below.
## <a name="_toc143028448"></a><a name="_toc143538397"></a>2.6 Exiting the System
**Proper Exit:** To exit the system, run ‘terraform destroy’ after navigating inside the ‘infrastructure’ folder. Before that, make sure to manually empty the ‘metadata-storage’ bucket in S3. Log out of your AWS account and close any open browser sessions.
## <a name="_toc143538398"></a>2.7 Summary of Usage
To summarize this section, to use our implementations, one would only need to follow the standard XC3 installation or the installation guide provided here. The only additional work that would need to be done is getting the Slack webhook url (steps are provided above). Other than that, the edits of the variables (which have to be done anyway, our variables are just added alongside them) and following the standard steps, the deployment of our features is automatic.













#






# <a name="_toc143538399"></a>3. <a name="_toc143023228"></a>Notification Services
In this section, we are first going to cover the individual lambdas that are to be used. Again, they are all automatically deployed with XC3. We are going to present the Lambda functions the integration of Cronjob and Cloudwatch, and the general integration into XC3. 

## <a name="_toc143023229"></a><a name="_toc143538400"></a>3.1 Total Account Cost Notifications
When integrated with XC3, my lambda is automatically deployed with XC3. No separate installation is necessary. To use it on its own, users can go to Amazon Web Services, go to Lambda, then Create Function where users can paste my code and use the provided policies to make it work.

To get Total Account Cot Notifications, the variables “budget”, “email address”, and “slack webhook url” need to be provided. “email address” variable needs to be provided to receive notifications via Email, and “slack webhook url” needs to be provided to receive notifications on Slack Channel. Without “email address”, and “slack webhook url” no message will be sent. It must be ensured that these 2 inputs are correct. The variable “budget” must be a number and not any string. This singular lambda performs the 3 tasks of getting cost metrics, pushing it to Cloudwatch for monitoring, and sending notification if budget is crossed.

The above code is my implementation. Making a new Lambda in AWS with this code will work if provide with the correct policies. The correct policies are:

![A screenshot of a computer program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.006.png)

*Figure 3 In-Line Policy 1*

![A screenshot of a computer code

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.007.png)

*Figure 4 In-Line Policy 2*

![A screenshot of a computer

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.008.png)

*Figure 5 In-Line Policy 3*

In our integration into XC3, the team was successfully able to implement all of the above by using Terraform files that were integrated with existing files of XC3. Users don’t need to add any of them manually. Those parts were implemented by other members of my team. My contribution was the above lambda function, its policies, and testing to make sure it works. Within my work, the budget, Slack Webhook URL, Email, policies, and resource arns are provided by me and are specific to my account. As stated, the implementations were made global by my team, the scope of which is outside of this document.

For the email service to work, the sender email will receive a verification email which must be followed through, otherwise email will not be sent from that address. For my implementation, the budget, slack webhook url, and email addresses have to be provided to the lambda itself. But, this is not necessary in our teams implementation. 

Below, there is a code snippet that shows a part of how Total Account Cost notification works:

![A computer screen shot of a program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.009.png)

*Figure 6 Code snippet for Total Account Cost*

In the above code example, I am extracting account cost from Cost Explorer, checking against my budget threshold, and sending Email via SES. For this code to work, it needs the policies shown in Figure 1, 2, and 3

## <a name="_toc143023230"></a><a name="_toc143538401"></a>3.2 Resource Cost Notifications
When the total modified XC3 of my team is used, no separate installation is necessary. To test or use just this Lambda, users can go to Amazon Web Services, Lambda, Create Function and paste my code and test it manually. However, a json file containing cost metrics must also be placed in a specific folder of a specific bucket as this Lambda uses data generated by XC3 default Lambdas. Therefore, for manual testing a json file of a specific structure must be placed in a specific folder of a S3 bucket

Just like the Total Cost Notification, this Resource Cost Notifications Lambda checks the cost, pushes metrics to Cloudwatch, and sends notification to Slack and Email if budget is crossed. One key difference is that, the cost metrics that are used this time are not generated from Cost Explorer but rather from a json file from the S3 bucket deployed with XC3. XC3 has other lambda functions that generates those cost metrics, formats then specifically and sends them to Prometheus and Grafana. My Resource Cost Notification Lambda was built to work alongside it and so therefore uses the cost metrics generated by XC3. 

To use test this Lambda, the variables “budget”, “email address”, and “slack webhook url” need to be provided. “email address” variable needs to be provided along with a variable of folder location. That location must also have the correct file. An example of the format of json file is provided below:

![](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.010.png)

Again, within XC3, no separate installation is necessary. In order to use this manually simply paste the code in Lambda section of Amazon Web Services. Before running, add the policies listed above as well as the following one:

![A screenshot of a computer code

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.011.png)

*Figure 7 In-Line Policy 4*






Below are some code snippet showing how it works:

![A computer screen with many lines of text

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.012.png)

*Figure 8 Code Snippet for Loading and Parsing through Data for Resource Notification*

![A screenshot of a computer program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.013.png)

*Figure 9 Calculating Resource Cost and generating Payload message*

In Figure 6, the code is reading the json file containing data and parsing through them. In Figure 7, it generates a payload or message if budget is crossed and send them to slack and email for notification
## <a name="_toc143023231"></a><a name="_toc143538402"></a>3.3 IAM User Notifications
When the total modified XC3 of my team is used, no separate installation is necessary. To test or use just this Lambda, users can go to Amazon Web Services, Lambda, Create Function and paste my code and test it manually. However, a json file containing cost metrics must also be placed in a specific folder of a specific bucket as this Lambda uses data generated by XC3 default Lambdas. Therefore, for manual testing a json file of a specific structure must be placed in a specific folder of a S3 bucket

To use test this Lambda, the variables “budget”, “email address”, and “slack webhook url” need to be provided. “email address” variable needs to be provided along with a variable of folder location. That location must also have the correct file. An example of the format of json file is provided below:

![](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.014.png)

Just like for Resource Cost Notification Lambda, the IAM User Notification also uses the data generated by XC3 default lambdas to get the metrics. It then checks the cost, pushes it to Cloudwatch, and sends Email and Slack messages if the budget is crossed.

Adding the 4 policies listed above from Figure 1, 2, 3, and 5 will make this lambda work. 

A code snippet of how this works is provided below:

![](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.015.png)

*Figure 10: IAM Cost Notification*

For IAM Cost Notification, data is read and parsed similarly as in Resource cost notification. Calculation for individual IAM user can be seen above and once payload is generated email and slack notification is sent

## <a name="_toc143090087"></a><a name="_toc143538403"></a>3.4 Cronjob
The cronjob allows users to schedule the events that can be repeated in a specific amount of time. The Cloudwatch Events and Amazon EventBridge components have been integrated into the infrastructure by defining Terraform resources. The purpose is to trigger the Lambda function at regular intervals using cron scheduling, allowing seamless execution of the IAM user cost management logic. The Terraform code establishes the necessary configurations as follows:

CloudWatch Events Rule for Cron Job:

![A computer screen shot of text

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.016.png)

*Figure 11: Event Rule for Cron Job*

The AWS CloudWatch Events rule, named "LambdaCronJobRule," is configured to trigger the Lambda function every minute for 24 hours using the cron expression "cron(0/1 \* \* \* ? \*)" which users can change accordingly.

CloudWatch Events Rule Target (Lambda Function):

![A screen shot of a computer program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.017.png)

*Figure 12: Event Rule Target*

The defined CloudWatch Events rule is associated with the Lambda function through the AWS CloudWatch Events target resource named "lambda\_target." This ensures that the Lambda function is invoked according to the defined schedule.










Lambda Function Permission for CloudWatch Events:

![A screen shot of a computer program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.018.png)

*Figure 13: Cloudwatch Events Rule Permission*

The "eventbridge\_permission" Lambda permission resource grants the necessary permissions for the CloudWatch Events rule to invoke the Lambda function. It specifies that the Lambda function can be invoked by the "events.amazonaws.com" principal and is linked to the CloudWatch Events rule's ARN.

Overall, the combination of these resources enables the Lambda functions to be executed automatically at the specified intervals using CloudWatch Events. This functionality streamlines the management of IAM user costs by ensuring consistent and timely execution of the relevant logic.

Through the Terraform setup, users can efficiently manage IAM user costs, control access to designated S3 buckets, utilize Simple Email Service (SES) for email communication, and gather essential CloudWatch metrics for monitoring purposes. This approach facilitates an organized and automated solution for IAM user cost management in AWS.
## <a name="_toc143538404"></a>3.5 <a name="_toc143090086"></a>Cloudwatch Integration
For Total Account Cost and IAM User, the cost metrics has been pushed to Cloud Watch for monitoring purpose. The Total Account Cost fetches data from the cost explorer while the IAM User fetches from the S3 bucket. Users can define their S3 bucket by providing arn for the cost metrics in the Resource variable. 

![A computer screen shot of a program code

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.019.png)

*Figure 14 : Cloudwatch Policy*

The Cloudwatch put metric policy has also been defined for both of the lambda functions in the terraform file which users can run without any modifications. The policy allows users to put the metrics into the cloudwatch for the costs and monitoring,

![A screen shot of a computer code

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.020.png)

*Figure 15: Cloudwatch put metric policy*


# <a name="_toc143028450"></a><a name="_toc143538405"></a>4 Integration
##
## <a name="_toc143538406"></a>4.1 Integrating python and terraform files
Effectively integrating Python and Terraform files within the XC3 project is important to maintain a well-structured and streamlined development process. 

1. Firstly, a comprehensive review of the contents is done to understand the functionality and requirements of the feature.
1. Then, the python file needs to be strategically placed within the ‘/src’ folder to ensure consistency of the files. 
1. ` `The terraform file is kept under ‘/infrastructure/modules/serverless/’ folder. Having similar files together ensures accessibility as well.

Note: Make sure the python and terraform files are renamed to a name that reflects their functionality.
## <a name="_toc143028451"></a><a name="_toc143538407"></a>4.2 Implementing Global Variables
Global variables play a pivotal role in maintaining consistency and modularity throughout the project. They allow us to define critical parameters, settings, and data once, ensuring that changes or updates are reflected uniformly across the system. This promotes code reusability, reduces redundancy, and simplifies maintenance.

**Approach and Implementation:** To implement global variables effectively, the existing code was carefully examined, then a structured approach was created, and then integrated. The implementation was gradual as the efficiency of the process needed to be measured.

1. Defining global values
   1. Go to ‘terraform.auto.tfvars’ file under xc3/infrastructure. Add a variable name and give it your desired value. All the variables defined in terraform.auto.tfvars are global variables. For example (budget\_amount = 25)![A screen shot of a computer program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.021.png)
   1. Now, go to variables.tf file under xc3/infrastructure and define the variable. For example: 

\# Define a variable for the budget amount

variable "budget\_amount" {

`  `type    = number

`  `default = 20 # Enter the budget amount here

}

1. Depending on which module you want the variable implementation in, define the variable in the variables.tf file of that folder as well. (For example: We want the budget\_amount in the modules/serverless folder. So, we define the variable in variables.tf file under the serverless folder as well.
1. Under main.tf, pass the defined value for the variable from terraform.auto.tfvars to the serverless folder. For example: in main.tf, under module “serverless”, 

budget\_amount = var.budget\_amount

var.budget\_amount takes data from terraform.auto.tfvars. Defining the values in main.tf under modules “serverless” ensures that the variable name budget\_amount can be used in any terraform file under the “serverless” folder under “modules” directory.

![A screenshot of a computer program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.022.png)

1. Using the global variables in terraform

Once the global variables are defined, they can be called by the terraform files. The syntax for calling is ‘var.{variable name}’. 

For example, in total\_account\_alert.tf, namespace can be used like:

\# Define the IAM role for the Lambda function

resource "aws\_iam\_role" "total\_account\_alert" {

`  `name = "${**var.namespace**}\_total\_account\_alert" # Here, the var.namespace gets      data from main.tf, which gets data from terraform.auto.tfvars

`  `assume\_role\_policy = jsonencode({

`    `Version = "2012-10-17",

`    `Statement = [

`      `{

`        `Action = "sts:AssumeRole",

`        `Effect = "Allow",

`        `Principal = {

`          `Service = "lambda.amazonaws.com"

`        `}

`      `}

`    `]

`  `})

}

1. Using the global variables in python file

The AWS Lambda function configuration defined in the Terraform file allows you to set environment variables that can be accessed within the associated Python code. This feature provides a seamless way to securely pass dynamic data and configuration parameters from Terraform to your Python code. 

\# AWS Lambda Function

resource "aws\_lambda\_function" "total\_account\_alert" {

`  `filename      = data.archive\_file.total\_account\_alert.output\_path

`  `function\_name = "${var.namespace}-TotalAccountAlert"

`  `role          = aws\_iam\_role.total\_account\_alert.arn

`  `handler       = "total\_account\_alert.lambda\_handler"

`  `runtime       = "python3.9"

`  `timeout       = 10  

`  `environment {

`    `variables = {

`      `BUDGET\_AMOUNT = var.budget\_amount

`      `SLACK\_WEBHOOK\_URL = var.slack\_channel\_url

`      `SES\_EMAIL\_ADDRESS = var.ses\_email\_address

`      `SNS\_TOPIC\_ARN = var.sns\_topic\_arn2

`    `}

`  `}

`  `publish = true

}

In the Terraform code snippet provided, you can see that we are setting multiple environment variables within the aws\_lambda\_function resource block. These variables, such as BUDGET\_AMOUNT, SLACK\_WEBHOOK\_URL, SES\_EMAIL\_ADDRESS, and SNS\_TOPIC\_ARN, are critical parameters required for the operation of the Lambda function.

These environment variables are then accessible within your Python code through the use of the os module. Here's an example of how you can access and use these variables within your Python code:

\# Set the budget amount and budget thresholds

budget\_amount = float(os.environ['BUDGET\_AMOUNT'])

threshold\_25 = budget\_amount \* 0.25

threshold\_50 = budget\_amount \* 0.5

threshold\_75 = budget\_amount \* 0.75

\# Set your Slack webhook URL

slack\_webhook\_url = os.environ['SLACK\_WEBHOOK\_URL']

By utilizing the os.environ[‘’] function, you can retrieve the values of the environment variables that you defined in the Terraform file. This approach ensures that sensitive information, configuration parameters, and dynamic data are securely passed to your Python code at runtime.

**Note**: In terraform files, make sure you provide dynamic names to the resources to avoid conflict with pre-existing resources.

resource "aws\_iam\_role" "total\_account\_alert" {

`  `name = "${var.namespace}\_total\_account\_alert"

resource "aws\_iam\_role" "total\_cost\_by\_service" {

`  `name = "${var.namespace}\_LambdaCostbyServicesRole"


For example, in the above snippet, the resource ‘aws\_iam\_role’ has been created in two different terraform files, but the name is different, i.e. ‘total\_account\_alert’ and ‘total\_cost\_by\_service’, which is unique to only the particular terraform file. Also, the name of the resource is made dynamic by adding the namespace in front of the actual name. This makes sure that there is no conflict with the resources that were already created. When there are redundant resources created in multiple occasions, it is good practice to provide unique names for easy access as well.





# <a name="_toc143023237"></a><a name="_toc143538408"></a>5. Troubleshooting

## <a name="_toc143023238"></a><a name="_toc143538409"></a>5.1 Common Issues and Solutions
### <a name="_toc143023239"></a><a name="_toc143538410"></a>5.1.1 Email Not Being Sent
One Issue that users may have is that they are not receiving Email. There are a few solutions to this:

- Check that the source and destination email addresses to see if spelling is correct
- Check the budget threshold to see if budget is too high and email is *not supposed* to be sent
- Make sure that the source email address is verified. When email is supposed to be sent, the source email address receives an email for authentication and verification. Verification must be done so that email is sent properly
- Check the SPAM folder to make sure that email is not automatically rerouted to SPAM
- The SNS/SES policy isn’t attached- this can include mistake of the SNS/SES arn
### <a name="_toc143023240"></a><a name="_toc143538411"></a>5.1.2 Slack Message Not Being
If messages are not being sent to slack try the following solutions:

- Check the budget threshold to see if budget is too high and slack message is *not supposed* to be sent
- Check the Slack API that was created by the user to see if permissions are properly given
- Check that the policies are attached properly
### <a name="_toc143023241"></a><a name="_toc143538412"></a>5.1.3 Bucket Access Denied
There are a few solutions if when running Lambda you get the Bucket Access Denied Policy

- Make sure that the file name, location are correct
- That the file exists in the correct location
- That the policy of bucket access is correctly attached (especially that \* symbol at the end)
### <a name="_toc143023242"></a><a name="_toc143538413"></a>5.1.4 Usage Access Denied 
If you are getting this message you can try the following solutions:

- Cost Explorer is enabled. For a new Amazon Web Services account, it can take upto 24 hours for it to be enabled (instructions are provided in the installation guide for enabling cost explorer)
- Policies are attached properly
### <a name="_toc143028453"></a><a name="_toc143538414"></a>5.1.5 Error Messages
In the event of encountering error messages, refer to the following table for likely causes and corrective actions:

|**Error Message**|**Likely Cause(s)**|**Corrective Action(s)**|
| - | - | - |
|Error: Budget Exceeded|Budget threshold exceeded|Review budget settings and adjust|
|Error: Invalid Slack Webhook URL|Incorrect Slack URL format|Verify and update the Slack URL|
|Error: Access Denied|Insufficient IAM permissions|Validate IAM roles and permissions|
|Error: Lambda Timeout|Execution time exceeded limit|Optimize code or increase timeout|
|<p>Error: deleting EventBridge Rule </p><p>(example-rule): ValidationException: </p><p>Rule can't be deleted </p><p>since it has targets. status code: 400, </p><p>request id: 6160fac7……</p>|<p>The EventBridge rule has associated targets.</p><p>The rule might still be referenced by other resources.</p><p></p>|<p>Identify the rule causing the error.</p><p>Remove all targets associated with the rule.</p><p>Ensure the rule is not referenced elsewhere.</p><p>Apply changes with terraform apply.</p><p>Proceed with terraform destroy.</p><p></p>|

### <a name="_toc143538415"></a>5.1.6 Issues with Terraform
Here's a troubleshooting guide for potential issues that might arise while working with the Terraform code.

**IAM Role and Policy Configuration:**

Issue: The IAM role or policies aren't created properly.

Troubleshooting: Double-check the IAM role and policy resources. Verify their names, JSON policy documents, and their associations. Make sure there are no typos or syntax errors.

**Lambda function Setup:**

Issue: Lambda function doesn't execute as expected.

Troubleshooting: Ensure the function's role, handler, runtime, filename, and timeout are correctly set. Verify that the function's ZIP file is generated and uploaded successfully.

**CloudWatch Events Rule:**

Issue: Lambda function isn't triggered by CloudWatch Events.

Troubleshooting: Review the CloudWatch Events rule configuration. Confirm that the schedule expression is valid. Check for any overlapping rules that might affect triggering.

**Lambda Function Permission:**

Issue: Permission issues causing CloudWatch Events not to invoke the Lambda.

Troubleshooting: Validate the "eventbridge\_permission" resource. Ensure the Lambda function's ARN and the CloudWatch Events rule's ARN are accurate. Verify that the principal is set to "events.amazonaws.com".

**AWS Provider Configuration:**

Issue: Resources fail to create due to incorrect AWS provider configuration.

Troubleshooting: Check the AWS provider configuration at the beginning of the code. Verify the specified region and other settings are accurate.

**General Errors:**

Issue: Resources fail to create due to various errors.

Troubleshooting: Examine the error messages returned by Terraform. These messages can provide insights into what went wrong. Review your code and make sure there are no missing or extra attributes, and all resource dependencies are properly defined.

**Permissions and Policies:**

Issue: Resources are created, but they don't behave as expected due to inadequate permissions.

Troubleshooting: Verify that the IAM roles and policies grant the necessary permissions to access required resources. Cross-check your permissions settings with the intended actions of each resource.

**Resource Naming Conflicts:**

Issue: Resources fail to create due to naming conflicts.

Troubleshooting: Ensure that resource names, such as IAM roles, policies, and Lambda functions, are unique within your AWS account and adhere to AWS naming conventions.

**Terraform State Management:**

Issue: Inconsistent state between local configurations and remote state.

Troubleshooting: Regularly run terraform init and terraform plan to refresh your local state with the remote state. If issues persist, consider using remote backends for state storage.

**API Rate Limits:**

Issue: Repeatedly executing Terraform commands causes AWS API rate limits to be exceeded.

Troubleshooting: Be mindful of your AWS API usage. If needed, consider requesting higher rate limits or using AWS Service Quotas to ensure sufficient limits for your resource provisioning.
## <a name="_toc143023243"></a><a name="_toc143538416"></a>5.2 FAQs
**Q1: What is the purpose of the Notification Services feature in XC3?**

A1: The Notification Services feature in XC3 provides users with the ability to receive timely alerts and notifications regarding their AWS account's budget and cost thresholds. This feature helps users stay informed about their account's spending to ensure budget compliance.

**Q2: How do I set up the Notification Services feature?**

A2: Setting up the Notification Services feature involves integrating the provided Lambda functions into your XC3 environment. The detailed installation process can be found in the "Getting Started" section of this manual. Additionally, you'll need to configure necessary variables such as budget, email addresses, and Slack webhook URLs.

**Q3: What are the system requirements for using the Notification Services feature?**

A3: To utilize the Notification Services feature, you need an Amazon Web Services (AWS) account. You'll also need to have Terraform, Python, AWS CLI, and certain permissions set up. The detailed list of system requirements can be found in the "System Requirements" section of this manual.

**Q4: How do I configure the Notification Services to send alerts via email and Slack?**

A4: To configure alerts, you need to provide the necessary variables such as budget, source email address, recipient email address, and Slack webhook URL (if applicable). These variables will be used by the Lambda functions to determine when to send notifications. Instructions for configuration can be found in the "Usage of Notification Service" section.

**Q5: Can I use the Notification Services feature on its own or only within XC3?**

A5: The Notification Services feature can be used both independently and as part of the XC3 environment. If using it independently, you can manually deploy the Lambda functions in AWS Lambda and set up the necessary variables. In XC3, the integration is already done, and you can take advantage of the feature seamlessly.

**Q6: How does the Cronjob setup work for the Notification Services feature?**

A6: Cronjob setup involves scheduling the Lambda functions to run at specific intervals. The detailed process can be found in the "Cronjob Setup" subsection of the "Notification Services" section. By following the outlined steps, you can ensure that the Lambda functions execute periodically.

**Q7: How do I troubleshoot common issues with the Notification Services feature?**

A7: The "Troubleshooting" section of this manual provides solutions to common issues you might encounter. From email not being sent to Slack messages not being delivered, we've compiled solutions for the most frequent problems users might face.

**Q8: Can I customize the Lambda functions for my specific needs?**

A8: Absolutely. The provided Lambda functions are modular and can be customized to suit your specific requirements. However, please exercise caution while modifying the code to ensure that the core functionality remains intact.

**Q9: What security considerations should I keep in mind when configuring the Notification Services feature?**

A9: When configuring the feature, ensure that you handle sensitive information such as email addresses and Slack webhook URLs securely. Additionally, follow AWS security best practices and consider the permissions and policies attached to the Lambda functions.

**Q10: Is this feature suitable for non-technical users?**

A10: While the Notification Services feature involves technical configurations, the provided instructions and code snippets are designed to be user-friendly. However, some familiarity with AWS services and basic cloud monitoring concepts will be beneficial.

**Q11: What is the purpose of this Terraform code?**

A11: This Terraform code is designed to automate the setup of resources for managing IAM user costs in AWS. It creates a Lambda function, sets up timed triggers using CloudWatch Events, and defines necessary permissions and policies.

**Q12: Can I use this code in different AWS regions?**

A12: Yes, you can modify the "region" value in the AWS provider configuration at the start of the code to specify your desired AWS region.

**Q13: How do I customize the budget amount for IAM user costs?**

A13: To customize the budget amount you can modify the budget amount by changing the value of the "budget" variable in the code. Locate the "variable" block named "budget" and update the "default" value to your desired budget.

**Q14: How do I change the execution frequency of the Lambda function?**

A14: The execution frequency is controlled by the CloudWatch Events rule. Locate the "aws\_cloudwatch\_event\_rule" resource named "lambda\_cron\_job." Modify the "schedule\_expression" value in the "schedule\_expression" attribute to set the desired execution frequency using a cron expression.

**Q15: What if my Lambda function is not triggering as scheduled?**

A15: First, ensure your CloudWatch Events rule is correctly configured with the desired schedule. Double check the Lambda function role and permissions that is using the "aws\_lambda\_function" resource and "aws\_lambda\_permission" resource. Verify that there are no conflicting rules.

**Q16: How can I control who can access S3 buckets and send emails using SES?**

A16: The code uses IAM policies to control access. For S3 bucket access, check the "aws\_iam\_policy" resource named "lambda\_policy." To control SES access, refer to the "aws\_iam\_role\_policy" resource named "ses\_policy." Adjust their policy documents to specify the desired permissions.

**Q17: How can I troubleshoot errors while deploying the code?**

A17: When errors occur, read the error messages carefully to understand what the issue is. Review the corresponding part of the code, verify resource names, permissions, and settings. Also, check if the AWS provider configuration is accurate.


**Q18: Can I adapt this code to trigger other Lambda functions at specific intervals?**

A18: You can modify this code to trigger other Lambda functions by adjusting the "aws\_cloudwatch\_event\_rule," "aws\_lambda\_function," and "aws\_lambda\_permission" resources accordingly, making sure to change function names and ARNs as needed.
# <a name="_toc143023245"></a><a name="_toc143538417"></a>6. Appendices

## <a name="_toc143023246"></a><a name="_toc143538418"></a>6.1 Sample Screenshots

### <a name="_toc143023247"></a><a name="_toc143538419"></a>Example of Email
![A screenshot of a computer

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.023.png)

*Figure 11 Example of the Email Sent via Lambda*
###
###
###
###
###
###
###
###
###

### <a name="_toc143023248"></a><a name="_toc143538420"></a>Example of Slack Message

![A screenshot of a computer

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.024.png)

*Figure 12 Example 1 of Slack Message Sent via Lambda*

![A screenshot of a computer

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.025.png)

*Figure 18 Example 2 of Slack Message sent via Lambda*
## <a name="_toc143023249"></a><a name="_toc143538421"></a>6.2 Code Snippets
In this section, I am going to add some code snippets and discus them accordingly.

<a name="_toc143023250"></a><a name="_toc143538422"></a>Code for Email

The following code is the most simplified code for sending message via email. This contains a very simplified message. I chose this example as it’s the least complex message that I am sending. It gets triggered if a threshold message is generated which only happens if a budget is crossed. A code snippet is provided below:

|<p>**if** threshold\_message:</p><p>`        `# Compose the email content</p><p>`        `email\_subject = "AWS Account Cost Threshold Alert"</p><p>`        `email\_body = f"The AWS account cost has crossed the {threshold\_message}."</p><p></p><p>`        `# Send the email using Amazon SES</p><p>`        `ses\_client = boto3.client('ses')</p><p>`        `ses\_client.send\_email(</p><p>`            `Source='zahinakram65@gmail.com',</p><p>`            `Destination={</p><p>`                `'ToAddresses': ['zahinakram65@gmail.com'],</p><p>`            `},</p><p>`            `Message={</p><p>`                `'Subject': {</p><p>`                    `'Data': email\_subject,</p><p>`                `},</p><p>`                `'Body': {</p><p>`                    `'Text': {</p><p>`                        `'Data': email\_body,</p><p>`                    `},</p><p>`                `}</p><p>`            `}</p><p>`        `)</p><p></p>|
| - |
###
###
### <a name="_toc143023251"></a><a name="_toc143538423"></a>Code for Slack

The following is the code for a very simple slack message. It uses the webhook url generated (guideline for generating it is provided). The code is only triggered if a threshold message is generated which happens only if a budget is crossed

|<p># Send the message to Slack via webhook</p><p>`        `webhook\_url = 'https://hooks.slack.com/services/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'</p><p>`        `slack\_message = {</p><p>`            `'text': f"The AWS account cost has crossed the {threshold\_message}."</p><p>`        `}</p><p>`        `req = urllib.request.Request(webhook\_url, data=json.dumps(slack\_message).encode('utf-8'), headers={'Content-Type': 'application/json'})</p><p>`        `response = urllib.request.urlopen(req)</p><p>`        `response.read()</p><p></p>|
| - |


<a name="_toc143023252"></a><a name="_toc143538424"></a>Code for Pushing metrics to Cloudwatch
----------------------------------------------------------------------------------------------

The following is the code for sending data to Cloudwatch. This is the most simple data that gets sent to Cloudwatch. It is just for the Total Cost. For Resource Notification and IAM Notification, the code for sending metrics to Cloudwatch is a bit more complicated. The simple example is shown below:

|<p># Publish the total cost metric to CloudWatch</p><p>`    `cloudwatch = boto3.client('cloudwatch')</p><p>`    `cloudwatch.put\_metric\_data(</p><p>`        `Namespace='AccountCost',</p><p>`        `MetricData=[</p><p>`            `{</p><p>`                `'MetricName': 'TotalCost',</p><p>`                `'Value': float(cost\_amount),</p><p>`                `'Unit': 'None'</p><p>`            `}</p><p>`        `]</p><p>`    `)</p><p></p>|
| - |
||




## <a name="_toc143538425"></a>Before/After files Integration
![A screenshot of a computer

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.026.png)

*Figure 13: Received .py and .tf files for total\_account\_alert function (before)*

![A screenshot of a computer program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.027.png)

*Figure 20: Put the .py files under appropriate folder in src directory and renamed them (after)*

![A screenshot of a computer program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.028.png)

*Figure 21:Put the .tf files under xc3/infrastructure/modules/serverless and renamed them (after)*

## <a name="_toc143028458"></a><a name="_toc143538426"></a>Before/After terraform file
![A screen shot of a computer program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.029.png)![A screen shot of a computer program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.030.png)

*Figure 22: Total Account Alert .tf file (Before) vs (After)*

The before file has provider “aws”, which becomes redundant because that is only needed in one .tf file. Also, the resource name for aws\_iam\_role is changed.

## <a name="_toc143028459"></a><a name="_toc143538427"></a>Before/After python file
![](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.031.png)![](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.032.png)![](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.033.png)![A computer screen shot of a program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.034.png)

![A computer screen shot of a program

Description automatically generated](pics/Aspose.Words.6de57d3a-3f54-442d-98e8-8252935ab3e1.035.png)

*Figure 23: Total Account Alert python file (Before) vs (After)*

` `We can see in the before file that the budget\_amount, slack\_webhook\_url, Source and ‘ToAddresses’ had hadrcoded variables. In after file, they are replaced by global variables.

