#!/usr/bin/env bash

# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Check if the AWS CLI is installed or not
if ! command -v aws &> /dev/null; then
    echo "----> AWS CLI is not installed."
    exit 1
else echo "AWS CLI is already installed. Moving forward..."
fi

# Check if terraform is installed or not
if ! command -v terraform &> /dev/null; then
    echo "----> Terraform is not installed."
    exit 1
else echo "Terraform is already installled. Moving forward..."
fi

# Check if pip3 is intalled or not
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Installing pip3..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
else
    echo "pip3 is already installed. Moving forward..."
fi

# Check if Python is installed or not
if ! command -v python3 &> /dev/null; then
    echo "----> Python is not installed."
    exit 1
else echo "Python is already installed. Moving forward..."
fi


# ************************************** User Inputs  ****************************************** #

namespace=$(grep 'namespace' input.sh | awk -F'"' '{print $2}')
if [ -z "$namespace" ]; then
    echo "----> The namespace variable is empty. Exiting the script..."
    exit 1
else
    echo "namespace:$namespace"
fi

project=$(grep 'project' input.sh | awk -F'"' '{print $2}')
if [ -z "$project" ]; then
    echo "----> The project variable is empty. Exiting the script..."
    exit 1
else
    echo "project:$project"
fi


region=$(grep 'region' input.sh | awk -F'"' '{print $2}')
if [ -z "$region" ]; then
    echo "----> The region variable is empty. Exiting the script..."
    exit 1
else
    echo "region:$region"
fi


allow_traffic=$(grep 'allow_traffic' input.sh | awk -F'"' '{print $2}')
if [ -z "$allow_traffic" ]; then
    echo "----> The allow_traffic variable is empty. Exiting the script..."
    exit 1
else
    echo "allow_traffic:$allow_traffic"
fi


domain=$(grep 'domain' input.sh | awk -F'"' '{print $2}')
echo "domain:$domain"

account_id=$(grep 'account_id' input.sh | awk -F'"' '{print $2}')
if [ -z "$account_id" ]; then
    echo "----> The account_id variable is empty. Exiting the script..."
    exit 1
else
    echo "account_id:$account_id"
fi


hosted_zone_id=$(grep 'hosted_zone_id' input.sh | awk -F'"' '{print $2}')
if [ -z "$hosted_zone_id" ]; then
    echo "----> The hosted_zone_id variable is empty. Exiting the script..."
    exit 1
else
    echo "hosted_zone_id:$hosted_zone_id"
fi


owner_email=$(grep 'owner_email' input.sh | awk -F'"' '{print $2}')
if [ -z "$owner_email" ]; then
    echo "----> The owner_email variable is empty. Exiting the script..."
    exit 1
else
    echo "owner_email:$owner_email"
fi


creator_email=$(grep 'creator_email' input.sh | awk -F'"' '{print $2}')
if [ -z "$creator_email" ]; then
    echo "----> The creator_email variable is empty. Exiting the script..."
    exit 1
else
    echo "creator_email:$creator_email"
fi


ses_email_address=$(grep 'ses_email_address' input.sh | awk -F'"' '{print $2}')
if [ -z "$ses_email_address" ]; then
    echo "----> The ses_email_address variable is empty. Exiting the script..."
    exit 1
else
    echo "ses_email_address:$ses_email_address"
fi


environ=$(grep 'env' input.sh | awk -F'"' '{print $2}')
environ=$(echo "$environ"|tr -d '\n')

if [ -z "$environ" ]; then
    echo "----> The environment variable is empty. Exiting the script..."
    exit 1
else
    echo "environment:$environ"
fi


bucket_name=$(grep 'bucket_name' input.sh | awk -F'"' '{print $2}')
if [ -z "$bucket_name" ]; then
    echo "----> The bucket_name variable is empty. Exiting the script..."
    exit 1
else
    echo "bucket_name:$bucket_name"
fi



#--------------- Pre_Requirement --> terraform.auto.tfvars --------------------#

# Namespace
pre_namespace=$(grep 'namespace' pre_requirement/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/namespace/ s/$pre_namespace/$namespace/g" pre_requirement/terraform.auto.tfvars

# Project
pre_project=$(grep 'project' pre_requirement/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/project/ s/$pre_project/$project/g" pre_requirement/terraform.auto.tfvars

# Creator Email
pre_creator_email=$(grep 'creator_email' pre_requirement/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/creator_email/ s/$pre_creator_email/$creator_email/" pre_requirement/terraform.auto.tfvars

# Owner Email
pre_owner_email=$(grep 'owner_email' pre_requirement/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/owner_email/ s/$pre_owner_email/$owner_email/" pre_requirement/terraform.auto.tfvars

# Region
pre_region=$(grep 'region' pre_requirement/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/region/ s/$pre_region/$region/" pre_requirement/terraform.auto.tfvars


#--------------- Infrastructure --> config.sh --------------------#


# Region
cur_region=$(grep 'aws_region' infrastructure/config.sh | awk -F'"' '{print $2}')

sed -i "/aws_region/ s/$cur_region/$region/" infrastructure/config.sh

# Project
cur_project=$(grep 'project' infrastructure/config.sh | awk -F'"' '{print $2}')

sed -i "/project/ s/$cur_project/$project/" infrastructure/config.sh

# Domain
cur_domain=$(grep 'domain' infrastructure/config.sh | awk -F'"' '{print $2}')

if [ "$cur_domain" == "" ]; then
    sed -i -e "s/domain=\"\"/domain=\"${domain}\"/g" infrastructure/config.sh
else
    sed -i "/domain/ s/$cur_domain/$domain/g" infrastructure/config.sh
fi

# Owner Email
cur_owner_email=$(grep 'owner_email' infrastructure/config.sh | awk -F'"' '{print $2}')

sed -i "/owner_email/ s/$cur_owner_email/$owner_email/g" infrastructure/config.sh

# Creator Email
cur_creator_email=$(grep 'creator_email' infrastructure/config.sh | awk -F'"' '{print $2}')

sed -i "/creator_email/ s/$cur_creator_email/$creator_email/g" infrastructure/config.sh

# NameSpace
cur_namespace=$(grep 'namespace' infrastructure/config.sh | awk -F'"' '{print $2}')

sed -i "/namespace/ s/$cur_namespace/$namespace/g" infrastructure/config.sh

# Bucket
cur_bucket_name=$(grep 'bucket_name' infrastructure/config.sh | awk -F'"' '{print $2}')

sed -i "/bucket_name/ s/$cur_bucket_name/$bucket_name/g" infrastructure/config.sh

#--------------- Infrastructure --> terraform.auto.tfvars --------------------#

# Namespace
infra_namespace=$(grep 'namespace' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/namespace/ s/$infra_namespace/$namespace/" infrastructure/terraform.auto.tfvars

# Environment
infra_env=$(grep 'env' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/env/ s/$infra_env/$environ/" infrastructure/terraform.auto.tfvars


# Region
infra_region=$(grep 'region' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/region/ s/$infra_region/$region/" infrastructure/terraform.auto.tfvars

# Account ID
infr_account_id=$(grep 'account_id' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/account_id/ s/$infr_account_id/$account_id/" infrastructure/terraform.auto.tfvars

# Domain for infra --> terraform.auto.tfvars
infra_domain=$(grep 'domain_name' infrastructure/terraform.auto.tfvars | awk -F'= ' '{print $2}')


if [ "$infra_domain" == '""' ]; then
     sed -i "/domain_name/ s/$infra_domain/\"$domain\"/" infrastructure/terraform.auto.tfvars
else
    sed -i "/domain_name/ s/$infra_domain/\"$domain\"/" infrastructure/terraform.auto.tfvars
fi

# Hosted Zone ID
infr_hosted_zone_id=$(grep 'hosted_zone_id' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/hosted_zone_id/ s/$infr_hosted_zone_id/$hosted_zone_id/" infrastructure/terraform.auto.tfvars


# SES Email Address
infr_ses_email_address=$(grep 'ses_email_address' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/ses_email_address/ s/$infr_ses_email_address/$ses_email_address/" infrastructure/terraform.auto.tfvars


# Creator Email
infra_creator_email=$(grep 'creator_email' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/creator_email/ s/$infra_creator_email/$creator_email/g" infrastructure/terraform.auto.tfvars

# Owner Email
infra_owner_email=$(grep 'owner_email' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/owner_email/ s/$infra_owner_email/$owner_email/g" infrastructure/terraform.auto.tfvars


# Project
infra_project=$(grep 'project' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/project/ s/$infra_project/$project/" infrastructure/terraform.auto.tfvars


# Allowed IPv4 Traffic
infra_allow_traffic=$(grep 'allow_traffic' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "s~$infra_allow_traffic~$allow_traffic~" infrastructure/terraform.auto.tfvars


# Envrionment
infra_environ=$(grep 'env' infrastructure/terraform.auto.tfvars | awk -F'"' '{print $2}')

sed -i "/env/ s/$infra_environ/$environ/" infrastructure/terraform.auto.tfvars

#--------------- Infrastructure --> backend.tf --------------------#


# Bucket
backend_bucket=$(grep 'bucket' infrastructure/backend.tf | awk -F'"' '{print $2}')

sed -i "/bucket/ s/$backend_bucket/$bucket_name/" infrastructure/backend.tf 

Region
backend_region=$(grep 'region' infrastructure/backend.tf | awk -F'"' '{print $2}')

sed -i "/region/ s/$backend_region/$region/" infrastructure/backend.tf 

#************************************** User Inputs  ******************************************#



# Do you want to create separate IAM role. Yes = Y or No = pres any key

while true; do

read -rp  "Do you want to create separate IAM role? (y/n) " yn

case $yn in
	[yY] )
		echo "Ok, we will proceed"
		cd pre_requirement || { echo "Failure : cd pre_requirement not working"; exit 1; }
		terraform init
		terraform fmt
		terraform apply -auto-approve
		echo "IAM role is created"
		cd ..
		break
		;;
	[nN] )
		echo "Proceeding without creating IAM Role...";
		break
		;;
	* )
		echo "Invalid response. Please enter 'y' for Yes or 'n' for No."
		;;
esac
done


# # Package the prometheus client library using following commands:
echo "Changing Dirctory: $(pwd)"
cd infrastructure || { echo "Failure : cd infrastructure not working"; exit 1; }
mkdir python
pip3 install -t python/ prometheus-client
zip -r python.zip ./python
echo "Packaging Prometheus Done"

# Running the bash pre_req.sh script
echo "Running pre_req.sh Script ... "
bash pre_req.sh || { echo "Failure : bash pre_req.sh not working"; exit 1; }
echo "pre_req.sh script is run successfully"


# # Deploying the infrastructure
terraform init

if ! terraform workspace select "$namespace"; then
    echo "Workspace $namespace does not exist. Creating..."
    terraform workspace new "$namespace"
else
    echo "Workspace $namespace already exists. Switching..."
    terraform workspace select "$namespace"
fi


terraform plan -var-file=terraform.auto.tfvars -out=tfplan.out

sleep 5

terraform apply "tfplan.out"

echo "XC3 Deployment is Done"
