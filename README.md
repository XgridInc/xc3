# X-CCC

Xgrid Cloud Cost Control is a cloud agnostic and risk free tool powered by Cloud Custodian that provides security enforcement, tagging, unused or invalid resources cleanup, account maintenance, cost control, and backups. It supports managing AWS public cloud environments and provides a visualization of usage of resources in account with support of managing resource utilization on a click. It spins up automation scripts and triggers lambdas to control cost of running resources in aws accounts and maintain state of each resource on which action performed having real-time visibility into who made what changes from where, enables us to detect misconfigurations and non-compliance. It supports rollback plans to prevent risks from materializing. Cloud Cost Control supports conditional policy execution. It generates reports, region vise and maintains state as well.

![x-ccc-architecture](https://user-images.githubusercontent.com/114464405/221472344-e68c94b1-d417-4c5f-96ed-4cf6dfac9e95.jpg)

## Objectives :

- One platform to track all your cloud resources be it cloud, multi-cloud, or hybrid infrastructure. It can track GCP, Azure, AWS resources on a single UI.

- It Enforces Tagging compliance that plays a vital role in determining the resources cost and many other aspects as well

- It provides Scheduled monitoring and alerting workflow that helps to track resource utilization and take action immediately.

- It provides cost optimization recommendation workflow without exposing your private information

## Benefits :

1. Cost Control of Resources
2. Resource Inventory
3. Off-hours/On-hours
4. Tagging Compliance
5. Garbage Collection
6. Tracks untagged & underutilized resources.
7. Security Compliance
8. Encryption
9. Backups

---

# X-CCC Architecture Diagram

![x-ccc-architecture](https://user-images.githubusercontent.com/114464405/221472344-e68c94b1-d417-4c5f-96ed-4cf6dfac9e95.jpg)

# To start using X-CCC

## Requirements

- [Terraform](https://www.terraform.io/downloads.html) 0.12+
- [Python](https://www.python.org/downloads) 3.7
- [AWScli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
- [Cloud Custodian](https://cloudcustodian.io/docs/quickstart/index.html#install-cloud-custodian)
- [Prometheus/Grafana/Pushgateway](https://github.com/Einsteinish/Docker-Compose-Prometheus-and-Grafana.git)

## Pre-requisites

1. Clone GitHub repo
   ` git clone https://github.com/X-CBG/X-CCC.git`
2. An AWS user with specific permission set user access.

   Refer the below IAM Permission Set to setup X-CCC.

   https://drive.google.com/drive/folders/1Cowx_VMHl4-ibOIHmM4498MPMlVXtkH_

3. A CodePipeline will be created in parent account where X-CCC infrastructure will be deployed.

   ![diagram-deployment](https://user-images.githubusercontent.com/114464405/221085370-091e92ba-9f0c-453b-9099-65a096fee2a5.jpeg)

4. VPC needs to be present in the parent account where you want to set up X-CCC
5. A Public and a Private subnet should be available.

   Use below AWS documentation to create subnets if necessary.

   https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-public-private-vpc.html

   Note : if no private/public subnets provided then X-CCC will create new VPC, private and public subnets and also X-CCC will destroy these resources once
   user destroys X-CCC setup.

6. X-CCC will create an EC2 instance during deployment, the user needs to create an AWS key_pair file in order to login to EC2 instance for troubleshooting purpose.
7. If the ssh access is restricted only through bastion/jump server/vpn, user should have the security group id of the bastion/jump/vpn EC2 instance.
8. The user has to **enable CostExplorer** by following the below link.

   https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ce-enable.html

   ```
   Note: After enabling CE, it may take up to 24hours for AWS to start capturing your AWS account cost data, hence X-CCC may not show the data until CE data is available in AWS account
   ```

# Deployment

X-CCC deployment will be done via a codepipeline that needs to be created in parent account which deploys the necessary EC2 instance , lambda functions and other related resources mentioned in architecture diagram in parent AWS account.

## Parent Account Deployment:

1. Clone the GitHub repo in your local computer if not done already and integrate it with CodePipeline to setup X-CCC infrastructure.
   ```bash
   git clone https://github.com/X-CBG/X-CCC.git
   ```
2. Following Steps will be done in CodePipeline Stages for deployment:

   1. `terraform.auto.tfvars` is the configuration file for the deployment. Use this files to create an `input.tfvars` file.

      Copy the mentioned configuration file and modify the parameters.

   2. Initialize Terraform. It will initialize all terraform modules/plugins. Before initializing the terraform user needs to export environment variables stored in .env file that will be used for grafana admin user credentials.
      go to `X-CCC/infrastructure/` directory and run below command

      ```bash
      cd X-CCC/infrastructure/
      source .env
      terraform init
      ```

      ````bash
      Expected Output: It will create .terraform directory in X-CCC/infrastructure/  location
                  Initializing modules...
                  - infrastructure in modules/networking
                  - infrastructure in modules/xccc
                  * provider.aws: version = "~> 4.0."
                  Terraform has been successfully initialized!
          ```

      ````

   3. Run planner command under `X-CCC/infrastructure` directory.

      ```bash
      terraform  plan -var-file=input.tfvars
      ```

      ```bash
      This command will generate a preview of all the actions which terraform is going to execute.
          Expected Output: This command will be giving output something like below
                  Plan: 20 to add, 0 to change, 0 to destroy.
                  ------------------------------------------------------------------------
      ```

   4. Run actual Apply command under `X-CCC/infrastructure` directory to deploy all the resources into AWS parent account.
      This step may take `10-15` mins.

      ```bash
      terraform apply -var-file=input.tfvars
      ```

      The output will look like below

      ```bash
          Expected output: It will ask for approval like below
              Do you want to perform these actions?
              Terraform will perform the actions described above.
              Only 'yes' will be accepted to approve.
              Enter a value:
      ```

      Please type "yes" and enter
      It provides the next steps to perform

      ```bash
      Apply complete! Resources: 20 added, 0 changed, 0 destroyed.

      Outputs:

      next_steps =
          Please run the following steps on deployed EC2 instance to trigger X-CCC.
          1. custodian run -s s3://${bucket_name}/iam-user/ --region ${aws_region} iam-user.yml
          2. custodian run -s s3://${bucket_name}/iam-role/ --region ${aws_region} iam-role.yml
          3. custodian run -s s3://${bucket_name}/expensive-service/ --region ${aws_region} most-expensive-service.yml --vars {expensive_service_lambda_function_name}

      ```

   5. Wait for few minutes before proceeding further for the application to come online.
      Verify the readiness of the metrics system. Load the Grafana URL in a browser. Live Grafana UI ensures the system is ready to accept and visualize metrics.

   > Verify the readiness of metrics system by accessing Grafana UI: https://xccc.xgrid.co/login

   Grafana default Credentials: default credentials are **"xgrid/xgrid@co"**

   6. Setup is complete here. Now X-CCC will run at 05:00AM UTC every day to generate data and populate Grafana.

      Note :  
       1. If data is not available in Grafana UI then follow the troubleshooting guide at the last section of this page.

# Troubleshooting Guide

case 1: If data is not showing into Grafana UI, there could be several reasons as shown below.

1. If AWS account was created freshly within last 24 hours then, you need to enable CostExplorer by following below link


    https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ce-enable.html


2. If the AWS account was created freshly within the last 24 hours then, it may take up to 24 hours for the AWS team to generate cost information in your account.
   you may see below error in lambda logs in Cloudwatch
   [ERROR] DataUnavailableException: An error occurred (DataUnavailableException) when calling the GetCostAndUsage operation: Data is not available. Please try to adjust the time period. If just enabled Cost Explorer, data might not be ingested yet
3. X-CCC Budget Detail/IAM Role/User Workflow lambda may have failed to execute , please check Cloudwatch logs to address the issue.

case 2: user not able to change/update/modify default dashboards in Grafana UI

1.  You can't change/update default dashboards.
2.  If you need to make changes, please clone new dashboards from the default dashboard JSON.

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
