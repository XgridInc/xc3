<br>

[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://github.com/XgridInc/xc3)
[![Slack](https://slackin.px.dev/badge.svg)](https://app.slack.com/client/T055VHJ0087/C0571UK3SBG)
[![Open AI Reviewer](https://github.com/XgridInc/xc3/actions/workflows/openai-pr-reviewer.yml/badge.svg)](https://github.com/XgridInc/xc3/actions/workflows/openai-pr-reviewer.yml)
[![Code Linter](https://github.com/XgridInc/xc3/actions/workflows/linter.yml/badge.svg)](https://github.com/XgridInc/xc3/actions/workflows/linter.yml)
[![Shellcheck](https://github.com/XgridInc/xc3/actions/workflows/shellcheck.yml/badge.svg)](https://github.com/XgridInc/xc3/actions/workflows/shellcheck.yml)
[![Code Vulnerability](https://github.com/XgridInc/xc3/actions/workflows/checkov.yml/badge.svg)](https://github.com/XgridInc/xc3/actions/workflows/checkov.yml)

<br>

# XC3

Xgrid Cloud Cost Control is a cloud agnostic and risk free package offering powered by Cloud Custodian that provides security enforcement, tagging, unused or invalid resources cleanup, account maintenance, cost control, and backups. It supports managing AWS public cloud environments and provides a visualization of usage of resources in account with support of managing resource utilization on a click. It spins up automation scripts and triggers lambdas to control cost of running resources in aws accounts and maintain state of each resource on which action performed having real-time visibility into who made what changes from where, enables us to detect misconfigurations and non-compliance. It supports rollback plans to prevent risks from materializing. Cloud Cost Control supports conditional policy execution. It generates reports, region vise and maintains state as well.

Check the below video for a quick demo of XC3.

[![XC3 Youtube](https://user-images.githubusercontent.com/114464405/229470468-ab186c9a-c475-40f2-9758-b89a7a3555d9.png)](https://www.youtube.com/watch?v=K4eEcl3wTZ0)

## Features

- One platform to track all your cloud resources be it cloud, multi-cloud, or hybrid infrastructure. It can track GCP, Azure, and AWS resources on a single UI.

- Enforces Tagging compliance that plays a vital role in determining the resources cost and many other aspects as well

- Provides Scheduled monitoring and alerting workflow that helps to track resource utilization and take action immediately.

- Provides cost optimization recommendation workflow without exposing your private information

# XC3 Architecture Diagram

![XC3-architecture](https://github.com/XgridInc/xc3/assets/105271892/47f7a162-eb39-43fd-b219-fe6cbddf78ec)

# To start using XC3

## Requirements

---

- [Terraform](https://www.terraform.io/downloads.html) 1.0+
- [Python](https://www.python.org/downloads) 3.9
- [AWScli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
- [Cloud Custodian](https://cloudcustodian.io/docs/quickstart/index.html#install-cloud-custodian)
- [Prometheus/Grafana/Pushgateway](https://github.com/Einsteinish/Docker-Compose-Prometheus-and-Grafana.git)
- [checkov](https://github.com/bridgecrewio/checkov) 2.0.574 or later
- [shellcheck](https://github.com/koalaman/shellcheck) 0.7.1 or later

## Pre-requisites

---

1. Clone GitHub repo
   ` git clone https://github.com/XgridInc/xc3.git`
2. An AWS user with specific permission set user access.

   Refer the IAM Permission Set created in `pre_requirement` folder to setup XC3.

3. VPC needs to be present in the master account where you want to set up XC3
4. A Public and a Private subnet should be available.

   Use below AWS documentation to create subnets if necessary.

   https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-public-private-vpc.html

   Note : if no private/public subnets provided then XC3 will create new VPC, private and public subnets and also XC3 will destroy these resources once
   user destroys XC3 setup.

5. To store terraform state and maintaing lock, S3 bucket and dynamodb should be available in master account.

6. ACM certificate should be available. It will be associated with loadbalanacer and domain.

7. XC3 will create an EC2 instance during deployment, the user needs to create an AWS key_pair file in order to login to EC2 instance for troubleshooting purpose.
8. If the ssh access is restricted only through bastion/jump server/vpn, user should have the security group ID of the bastion/jump/vpn EC2 instance.
9. The user has to **enable CostExplorer** by following the below link.

   https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ce-enable.html

   ```
   Note: After enabling CE, it may take up to 24hours for AWS to start capturing your AWS account cost data, hence XC3 may not show the data until CE data is available in AWS account
   ```

# Deployment

1.  Clone the GitHub repository in your local computer to setup XC3 infrastructure.

    ```
    git clone https://github.com/XgridInc/xc3.git
    ```

2.  You have to configure the config.sh file in xc3/infrastructure and run the below command
    ```
    cd xc3/infrastructure
    bash init.sh
    ```
3.  Install the `prometheus-client` library using following commands:
    ```
    cd infrastructure
    mkdir python
    cd python
    pip3 install prometheus-client -t
    cd ..
    zip -r python.zip ./python
    ```
4.  `terraform.auto.tfvars` is the configuration file for the deployment. Use this files to create an `input.tfvars` file.
    Copy the mentioned configuration file and modify the parameters.

5.  Initialize Terraform. It will initialize all terraform modules/plugins.
    go to `xc3/infrastructure/` directory.

    ```
    cd xc3/infrastructure/
    ```

    And run the following command

    ```
    terraform init
    ```

    `Expected Output: It will create .terraform directory in xc3/infrastructure/  location
        Initializing modules...
        - infrastructure in modules/networking
        - infrastructure in modules/xc3
        * provider.aws: version = "~> 4.0."
        Terraform has been successfully initialized!
`

6.  Run planner command under `XC3/infrastructure` directory.

    ```bash
    terraform  plan -var-file=input.tfvars
    ```

        ```bash
        This command will generate a preview of all the actions which terraform is going to execute.
            Expected Output: This command will be giving output something like below
                    Plan: 20 to add, 0 to change, 0 to destroy.
                    ------------------------------------------------------------------------
        ```

7.  Run actual Apply command under `xc3/infrastructure` directory to deploy all the resources into AWS master account.
    This step may take `10-15` mins.

    ```bash
    terraform apply -var-file=input.tfvars
    ```

    The output will look like below

    ````bash
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
    ````

8.  Please copy msg_templates in custodian directory on deployed EC2 instance

    ```
    sudo scp -r -i "keypair.pem" keypair.pem user@bastion-host-DNS:/directory-to-copy-keypair

    sudo scp -r -i "keypair.pem" ../cloud_custodian_policies/  user@bastion-host-DNS:~/.

    ssh -i "keypair.pem" user@bastion-host-DNS

    cd directory (where keypair copied in above command)

    sudo scp -r -i "keypair.pem" cloud_custodian_policies/ user@private-ip-ec2:~/.

    ssh -i "keypair.pem" user@private-ip-ec2

    sudo chown root:root /home/ubuntu/cloud_custodian_policies/msg_templates/*.html.j2

    sudo cp /home/ubuntu/cloud_custodian_policies/msg_templates/*.html.j2 /custodian/lib/python3.8/site-packages/c7n_mailer/msg-templates/

    ```

9.  Please run the following steps on deployed EC2 instance to trigger XC3 lambda functions.

    ```
        source /custodian/bin/activate
        cd cloud_custodian_policies

     1. custodian run -s s3://${bucket_name}/iam-user --region ${aws_region} iam-user.yml

     2. custodian run -s s3://${bucket_name}/iam-role/ --region ${aws_region} iam-role.yml

     3. custodian run -s tagging-compliance --region ${aws_region} eks-tagging.yml --region all


    ```

10. Wait for few minutes before proceeding further for the application to come online.
    Verify the readiness of the metrics system. Load the Grafana URL in a browser. Live Grafana UI ensures the system is ready to accept and visualize metrics.


    > Verify the readiness of metrics system by accessing Grafana UI: https://xc3.xxx.com/login

    > Verify the readiness of metrics system by accessing Grafana UI: `loadbalancer-dns`. If Hosted zone ID is not provided in `input.tfvars`.

11. Now User needs to upload grafana dashbords on S3 bucket created for metadata storage in above step.
    ```bash
    cd custom_dashboard
    aws s3 cp grafana_dashboards s3://${aws_s3_bucket}/content/ --recursive --exclude "*.md"
    ```
12. SSH into EC2 instance via Bastion host server and copy grafana dashboards from S3 bucket to local path using following commands:
    ```bash
    scp -i "xc3-key" xc3-key bastion-host-public-dns:/home/ubuntu/
    sudo ssh -i "xc3-key" ubuntu@public-ip of bastion host server
    cd /home/ubuntu
    sudo ssh -i "xc3-key" ubuntu@private-ip of prometheus server
    aws s3 cp s3://${s3_bucket}/content/ ~/content --recursive
    ```
13. Now setup is complete.Users needs to be added in Cognito pool with requested role (admin/editor/viewer) in respective cognito group. User get random username/password from cognito then you can set password on domain by sign in using random credentials.

14. Now XC3 will run at 05:00AM UTC every day to generate data and populate Grafana. Few lambdas (Total Account Cost and Project spend) will run twice in a month.

        Note :
            1. If data is not available in Grafana UI then follow the troubleshooting guide at the last section of this page.

# Troubleshooting Guide

case 1: If data is not showing into Grafana UI, there could be several reasons as shown below.

1. If AWS account was created freshly within last 24 hours then, you need to enable CostExplorer by following below link

   https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ce-enable.html

2. If the AWS account was created freshly within the last 24 hours then, it may take up to 24 hours for the AWS team to generate cost information in your account.
   you may see below error in lambda logs in Cloudwatch

   [ERROR] DataUnavailableException: An error occurred (DataUnavailableException) when calling the GetCostAndUsage operation: Data is not available. Please try to adjust the time period. If just enabled Cost Explorer, data might not be ingested yet

3. XC3 Budget Detail/IAM Role/User Workflow lambda may have failed to execute , please check Cloudwatch logs to address the issue.

case 2: user not able to change/update/modify default dashboards in Grafana UI

1.  You can't change/update default dashboards.
2.  If you need to make changes, please request for access for Editor/Admin role on

<br clear="all">

## Contibutor

XC3 is a community-driven project; we welcome your contribution! For code contributions, please read our [contribution guide](./CONTRIBUTING.md).

- File a [GitHub issue](https://github.com/XgridInc/xc3/issues) to report a bug or request a feature.
- Join our [Slack](https://join.slack.com/t/xgrid-group/shared_invite/zt-1uhzlrt6t-Dx_BqfQJKsHhSug1arbbAQ) for live conversations and quick questions.

<br clear="all">

## RoadMap

We welcome feedback and suggestions from our community! Please feel free to create an issue or join our discussion forum to share your thoughts.
For project updates, please read our [roadmap guide](./ROADMAP.md).

## License

XC3 is licensed under [Apache License, Version 2.0](./LICENSE).
