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

# This script creates an S3 bucket to store the Terraform state file,
# enables public block access on the S3 bucket, creates a DynamoDB table
# to maintain a lock on Terraform states, creates an EC2 key pair, and
# requests an ACM certificate that will be used in a Route 53 domain.
# KMS key that will be used for data encryption in cloudtrail configuration.
# It uses the values specified in the `config.sh` file to perform the necessary operations.
# The `config.sh` file should define the following variables:
#   - `aws_region`: The AWS Region to use for the resources created by this script.
#   - `dynamo_table_name`: The name to use for the DynamoDB table that will maintain a lock on Terraform states.
#   - `bucket_name`: The name to use for the S3 bucket that will store the Terraform state file.
#   - `project`: The project name to use as the tag value for the `Project` key to follow tagging compliance best practices.
#   - `domain`: The domain name to use when creating an ACM certificate that will be used in a Route 53 domain.
#   - `owner_email`: The email address of the owner of the team.
#   - `creator_email`: The email address of the creator who is spinning up the infrastructure.

CONFIG_FILE="./config.sh"

# Load the config.sh file
if [ -f "$CONFIG_FILE" ]; then
    # shellcheck source=./config.sh
    # shellcheck disable=SC1091
    source "$CONFIG_FILE"
else
    echo "Error: config.sh file not found"
    exit 1
fi

# shellcheck disable=SC2154
# AWS Region from config.sh to be used in rest of script
echo "AWS Region: $aws_region"
# shellcheck disable=SC2154
# Dynamodb Table Name to be used in creating dynamo db table for maintaining lock in terraform
# shellcheck disable=SC2154
echo "DynamoDB Table Name: $dynamo_table_name"
# shellcheck disable=SC2154
# S3 Bucket Name that will be used in creating S3 bucket for maintaining state file of terraform
# shellcheck disable=SC2154
echo "Bucket Name: $bucket_name"
# shellcheck disable=SC2154
# Project Name that will be used Tag value for Project key to follow tagging compliance best practices
# shellcheck disable=SC2154
echo "Project: $project"
# shellcheck disable=SC2154
# Domain Name to be used in create ACM Certificate that will be used in creating Route53 Domain
# shellcheck disable=SC2154
echo "Domain: $domain"
# shellcheck disable=SC2154
# Email Address of Owner of Team
# shellcheck disable=SC2154
echo "Owner Email: $owner_email"
# shellcheck disable=SC2154
# Email Address of Creator who is spinning up the infrastructure
# shellcheck disable=SC2154
echo "Creator Email: $creator_email"
# shellcheck disable=SC2154
# Email Address of Creator who is spinning up the infrastructure
# shellcheck disable=SC2154
echo "Namespace: $namespace"

# Create S3 bucket to store terraform state file in specific AWS Region
if aws s3api head-bucket --bucket "${bucket_name}" --region "${aws_region}" >/dev/null 2>&1; then
    echo "S3 bucket ${bucket_name} already exists"
else
    if aws s3api create-bucket --bucket "${bucket_name}" --region "${aws_region}" --create-bucket-configuration LocationConstraint="${aws_region}" && \
       aws s3api put-bucket-versioning --bucket "${bucket_name}" --versioning-configuration Status=Enabled --region "${aws_region}" && \
       aws s3api put-bucket-encryption --bucket "${bucket_name}" --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}' --region "${aws_region}"
    then
        echo "S3 bucket ${bucket_name} created successfully"
    else
        echo "Failed to create S3 bucket ${bucket_name}"
    fi
fi


# Enable public block access on S3 bucket
if aws s3api put-public-access-block --bucket "${bucket_name}" --region "${aws_region}" --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" > /dev/null; then
  echo "Successfully executed put-public-access-block command"
else
  echo "Error executing put-public-access-block command"
fi

# Create Dynamodb Table to maintain lock on terraform states
if aws dynamodb describe-table --table-name "${dynamo_table_name}" --region "${aws_region}" >/dev/null 2>&1; then
    echo "DynamoDB table ${dynamo_table_name} already exists"
else
    if aws dynamodb create-table \
        --table-name "${dynamo_table_name}" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
        --tags Key=backup,Value=short \
        --region "${aws_region}"; then
        echo "DynamoDB table created successfully"
    else
        echo "Error creating DynamoDB table"
    fi
fi


# Create EC2 Key-Pair that will be used to ssh into EC2 instances spin up by terraform module
if aws ec2 describe-key-pairs --key-names "${namespace}-key" --region "${aws_region}" >/dev/null 2>&1; then
    echo "Key pair ${namespace}-key already exists"
else
    if aws ec2 create-key-pair --key-name "${namespace}-key" --tag-specifications "ResourceType=key-pair,Tags=[{Key=Project,Value=${project}},{Key=Owner,Value=${owner_email}},{Key=Creator,Value=${creator_email}}]" --query 'KeyMaterial' --output text > "${project}"-key.pem --region="${aws_region}" ; then
        echo "Key pair created successfully"
    else
        echo "Error creating key pair"
    fi
fi


# Create ACM Certificate that will be used in Route 53 Domain
if [[ -z "${domain}" ]]; then
    echo "Domain is null. Skipping ACM certificate request."
else
    if aws acm request-certificate \
        --domain-name "${domain}" \
        --validation-method DNS \
        --key-algorithm RSA_2048 \
        --region "${aws_region}" \
        --tags "[{\"Key\":\"Project\",\"Value\":\"${project}\"}, {\"Key\":\"Owner\",\"Value\":\"${owner_email}\"}, {\"Key\":\"Creator\",\"Value\":\"${creator_email}\"}]" >/dev/null 2>&1; then
        echo "ACM certificate requested successfully"
    else
        echo "Failed to request ACM certificate"
    fi
fi
