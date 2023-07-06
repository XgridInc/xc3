This script is designed to automate the setup and deployment of infrastructure using AWS CLI, Terraform, and Python. It checks for the presence of required tools and prompts for user inputs to configure the deployment.

## Prerequisites
Before running the script, ensure that the following dependencies are installed:

- AWS CLI
- Terraform
- Python 3

If any of these dependencies are not installed, the script will exit with an error message.

## User Inputs
The script reads user inputs from the input.sh file. Ensure that the required variables are properly defined in this file:

- `namespace`: The namespace for the deployment.
- `project`: The project name.
- `region`: The AWS region to deploy the infrastructure.
- `allow_traffic`: Allowed IPv4 traffic.
- `domain`: The domain for the infrastructure.
- `account_id`: AWS account ID.
- `hosted_zone_id`: Hosted Zone ID for the domain.
- `owner_email`: Email address of the owner.
- `creator_email`: Email address of the creator.
- `ses_email_address`: SES email address.

## Pre-Requirements
The script performs some pre-configuration steps before deploying the infrastructure. It updates the `pre_requirement/terraform.auto.tfvars` and `infrastructure/config.sh` files with the user inputs.


## Creating Separate IAM Role
The script prompts the user to decide whether to create a separate IAM role. If the user chooses to create a separate IAM role, it executes Terraform commands in the `pre_requirement directory` to create the IAM role.

## Packaging Prometheus Client Library
The script creates a `python` directory within the `infrastructure` directory and installs the Prometheus client library using `pip3`. It then packages the python directory into a `python.zip` file.

## Running the init.sh Script
The script runs the `init.sh` script, which performs additional initialization steps for the deployment.


## Infrastructure Deployment
The script deploys the infrastructure using Terraform. It first checks if a Terraform workspace with the specified namespace exists. If the workspace does not exist, it creates a new one. Otherwise, it switches to the existing workspace.

The infrastructure is deployed by executing the following steps:

1. Initializes Terraform.
2. Plans the infrastructure changes and generates a plan file.
3. Applies the plan to create or update the infrastructure.


## Deployment Completion
Once the script completes the deployment process, it displays the message "XC3 Deployment is Done."

Note: Ensure that you have the necessary permissions and configurations set up for the AWS CLI and Terraform to run successfully.

Feel free to modify the script and files according to your specific requirements and configurations.