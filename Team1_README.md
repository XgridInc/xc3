**Table of Contents**

[Table of Contents](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.eb5cksptyvuz)

[Installation Steps:](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.30j0zll)

[Pre\_Req:](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.u26y3oey68cl)

[Cloning the Repo:](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.vl59lvq7d94g)

[Packaging the Prometheus:](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.6rwnip79g3nn)

[Deployment:](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.p9r0n8kgnh6)

[● Trigger IAM Role/User Workflow](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.u1zt1cd3bj3p)

[Pre-cautions:](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.vatpfbh0j222)

[Testing Lambda functions](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.dndo2f9lpp0)

[● List\_linked\_accounts

 Function Name: "{namespace}-list\_linked\_accounts"
 Click on "Test" and configure a test with the default test json, give the name to your test and run it.](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.mtcis2dhksu9)

[View the Dashboard](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.ufgfdp7e2dz8)

[Checking Prometheus Metrics](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.8xykl9nouwy4)

[Contributing in the Repo](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.jp69yyuke0zb)

[Enhancement in existing workflow](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.d1tzfv1i8xku)

[Adding a new workflow](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.wkuln0tn1bro)

[How to contribute](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.aofal24ikd22)

[Communication channel](https://docs.google.com/document/d/1YoaWoDSOjdOY2Wk3FXYHOni4wERCU7_WvsQamYkqS_o/edit#heading=h.gsgdi03hfymo)

**Installation Steps:**

**Pre\_Req:**

- Terraform ( Version 1.4.6) should be Installed, if not then you can install using: [Terraform Link](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- Python (Version 3.9) should be Installed, if not then you can install using : [Python Link](https://www.python.org/downloads/)
- AWS CLI (Version 2) should be Installed, if not then you can install using : [AWS CLI Link](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Configure AWS CLI (Your terminal should be able to access AWS Secret Key and Access Key) : [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- The user has to enable the CostExplorer API in their AWS Account by using the following link below. [AWS Cost Explorer](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ce-enable.html)

**Cloning the Repo:**

| git clonehttps://github.com/AamodPaud3l/Team1\_Alert.git |
| --- |

**Packaging the Prometheus:**

- **Package the prometheus client library using following commands** :

| cd xc3/infrastructure/
mkdir python
pip3 install -t python/ prometheus-client
zip -r python.zip ./python |
| --- |

**Deployment:**

1. **Go to xc3/pre\_requirement and update the variables in the terraform.auto.tfvars file**

cd xc3/pre\_requirement/

![](RackMultipart20230821-1-5gsj4a_html_61d706a97898f6f.png)

**Edit Line numbers 38-42 for the use of the alert feature , implemented by us**

**after modifying, run the below commands:**

| terraform initterraform plan -var-file=terraform.auto.tfvarsterraform apply -var-file=terraform.auto.tfvars |
| --- |

1. **Go to xc3/infrastructure/ and update the variables in the config.sh file.**

| cd xc3/infrastructure/ |
| --- |

![](RackMultipart20230821-1-5gsj4a_html_9a259077e00f06a6.png)

1. **After configuring the config.sh file in the xc3/infrastructure folder and run the commands mentioned below: **

|     bash pre-req.sh     chmod 400 "keypair.pem" |
| --- |

1. **Configure the bucket  in backend.tf file in xc3/infrastructure/, bucket names should be same in config.sh and backend.tf**

![](RackMultipart20230821-1-5gsj4a_html_dcf6a78557689d90.png)

1. **Configure the terraform.auto.tfvars file in xc3/infrastructure/**

![](RackMultipart20230821-1-5gsj4a_html_f761da861029a9df.png)

**Variables to configure:**

| **Variable** | **Standard** |
| --- | --- |
| **namespace** | Should be lowercase and unique
 e.g. **xc3** |
| **env** | Should be an environment where deployment will be done e.g. **dev** |
| **project** | The name of the project. It can be for any individual or group. It should be lowercasee.g. **xc3** |
| **creator\_email** | Email address of the individual provisioning the resource. (Add personal email) |
| **owner\_email** | Email address of the individual or team provisioning the resource. (Add personal email) |
| **account\_id** | The account ID for your AWS account |
| **domain\_name** | Domain name for the grafana dashboard (Optional, Not Recommended) |
| **hosted\_zone\_id** | Hosted Zone ID copied from Route 53(Optional, Not Recommended)  |
| **ses\_email\_address** | Email address of the individual provisioning the resource (Add personal email) |
| **region** | The region you want your resources to be provisioned in.
**Note:** Update the Availability zones values in the Private subnet and public subnet according to the region. ![](RackMultipart20230821-1-5gsj4a_html_e4453f4555c46db9.png) |

1. **After configuring the .tfvars files, we can run the following commands**

| terraform initterraform workspace new "unique\_name"terraform plan -var-file=terraform.auto.tfvarsterraform apply -var-file=terraform.auto.tfvars |
| --- |

- Enter " **yes**" to apply the infrastack
- Check the lb dns to verify that the infra is deployed successfully

**Note** : There will be a EC2 instance in the public subnet

**You can login in to Ec2 using the below command**

1. **SSH into EC2**

| ssh -i "keypair.pem" user@public-ip-ec2 |
| --- |

- _Trigger IAM Role/User Workflow_

**Please run the following steps on deployed  EC2 instance in /home/ubuntu/cloud\_custodian\_policies directory to trigger XC3 lambda functions.**

| source /custodian/bin/activatecd cloud\_custodian\_policiescustodian run -s tagging-compliance --region ${aws\_region} eks-tagging.yml --region all(optional) |
| --- |

- Cancel the ssh sessions and stop the bastion EC2 instance from the AWS Console.

**Pre-cautions:**

- By default, there is no .terraform folder; it will be created after running the terraform commands.
- Don't delete the **.terraform** folder and **.terraform.lock.hcl** file from xc3/infrastructure/ folder after you've run the terraform commands.
- Don't delete the **tfstate file** from your S3 backend bucket (mentioned in xc3/infrastructure/backend.tf).
- Don't run the **init\_delete.sh** script unless you want to destroy the fully deployed infrastructure and have run the following command.

|     terraform destroy |
| --- |

**Testing Lambda functions**

If you want to see immediate data on the dashboards then you can follow the steps mentioned below.

- _**List\_linked\_accounts

 Function Name: "{namespace}-list\_linked\_accounts"**_

 _Click on "Test" and configure a test with the default test json, give the name to your test and run it._

![](RackMultipart20230821-1-5gsj4a_html_559727a5abb4dea4.png)

-  _**Total-Account-cost
 Function Name: " **_** {namespace}-total\_account\_cost"**
 _Click on "Test" and configure a test with the default test json, give name to your test and run it._

![](RackMultipart20230821-1-5gsj4a_html_c142b8908648ff34.png)

-  _**Projects-Spend-cost
 Function Name: **_**"{namespace}-project-spend-cost"**
 _Click on "Test" and configure a test with the default test json, give name to your test and run it._ ![](RackMultipart20230821-1-5gsj4a_html_2b8ac82cc8dcb357.png)

-  _ **Most-expensive-service-lambda** _
_ **Function Name:** _ **"{namespace}-most\_expensive\_service\_lambda"**
 _Click on "Test" and configure a test with the default test json, give name to your test and run it._

![](RackMultipart20230821-1-5gsj4a_html_6f773d396dca216a.png)

_ **Total-Account-Alert-Lambda** _
_ **Function Name:** _ **"{namespace}-TotalAccountAlert"**
 _Click on "Test" and configure a test with the default test json, give name to your test and run it._

![](RackMultipart20230821-1-5gsj4a_html_c24d81a8febd10f.png)

_ **Total-Cost-by-Service-Lambda** _
_ **Function Name:** _ **"{namespace}-TotalCostByService"**
 _Click on "Test" and configure a test with the default test json, give name to your test and run it._

![](RackMultipart20230821-1-5gsj4a_html_b443644e154468a1.png)

_ **Total-Cost-by-IAM-User-Alert-Lambda** _
_ **Function Name:** _ **"{namespace}-iam\_user\_cost"**
 _Click on "Test" and configure a test with the default test json, give name to your test and run it._

![](RackMultipart20230821-1-5gsj4a_html_a1b8fd7f415bff02.png)

**View the Dashboard**

- Go to the ec2 Public-ip:3000
- Use the HTTP Protocol
- Login to the dashboard with Grafana Default Credentials
  - Username: **admin**
  - Password: **admin**

![](RackMultipart20230821-1-5gsj4a_html_75f83c42b9beb5ca.jpg)

**Checking Prometheus Metrics**

- **Run the following command in your private EC2 instance:**

curl[http://localhost:9091/metrics](http://localhost:9091/metrics)

**Contributing in the Repo**

**Enhancement in existing workflow**

![](RackMultipart20230821-1-5gsj4a_html_e708108b1a98e0d6.png)

**Adding a new workflow**

![](RackMultipart20230821-1-5gsj4a_html_bac2e3e8e0d88271.png)

**How to contribute**

- **Create feature branch after forking the repo**

git checkout -b branch-name

- **Configure** [**pre-commit hooks**](https://github.com/XgridInc/xc3/tree/develop/pre-commit-config)
  - Install the following in your system (pre-commit\>=2.0.0)

cd \<repo\_directory\>

pip install pre-commit

- Usage Instructions

  - Install the pre-commit hooks in your repository home directory:

pre-commit install -f --config pre-commit-config/.pre-commit-config.yaml

- **Adding files and committing**
  - git add
  - git commit -s ![](RackMultipart20230821-1-5gsj4a_html_abbcb1a099f40a0.png)

- git push

- **Create a PR from your feature branch to our** [**develop**](https://github.com/XgridInc/xc3/tree/develop) **branc** h
- **Unit tests will run**
- **PR Review SLA process**
  - The PR will be reviewed within 24 hours.




- **In order for a PR to be merged the following checkboxes are to be filled**
  - A proper description of the PR
  - The code must be tested before testing
  - The backend of the feature/enhancement must be present in the PR
  - The code PR must pass all the unit tests
  - The PR should have at least 4 approvals from our team
  - Add relevant details and screenshots in the PR

**Communication channel**

**The Communication channel is the** [**#general**](https://xc3community.slack.com/archives/C055VHJ1YLX) **channel on** [**Slack**](https://join.slack.com/t/xc3community/shared_invite/zt-1x0j80elv-ExpinY4Fp8XNgyP6nVZFNg)

- **Format of Reporting an Issue**
  - Mention which type of Issue it is, Deployment, XC3 Workflow
  - Give a complete description of the issue you are facing
  - Give the link of the GItHub Issue
  - Attach screenshots from Terminal or AWS Console

![](RackMultipart20230821-1-5gsj4a_html_315b05a45daf2324.png)
