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

# This script is used to delete AWS resources created by a init.sh script.
# It uses a configuration file 'config.sh' to retrieve the names and ARNs of the resources to delete.
# The configuration file should define the following variables:
# - aws_region: the AWS region where the resources were created.
# - dynamo_table_name: the name of the DynamoDB table to delete.
# - bucket_name: the name of the S3 bucket to delete.
# - namespace: the namespace used to create the resources.
# - Domain: the domain name used to create the ACM certificate.
# - owner_email: the email address of the owner of the team.
# - creator_email: the email address of the creator who spin up the resources.

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
# Dynamodb Table Name to be used in deleting dynamo db table
# shellcheck disable=SC2154
echo "DynamoDB Table Name: $dynamo_table_name"
# shellcheck disable=SC2154
# S3 Bucket Name that will be used in deleting S3 bucket
# shellcheck disable=SC2154
echo "Bucket Name: $bucket_name"
# shellcheck disable=SC2154
# Project Name that will be used Tag value for Project key to follow tagging compliance best practices
# shellcheck disable=SC2154
echo "Project: $project"
# shellcheck disable=SC2154
# Domain Name to create ACM Certificate that will be used in creating Route53 Domain
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
# Namespace who is spinning up the infrastructure
# shellcheck disable=SC2154
echo "Namespace: $namespace"



# Delete S3 bucket that was used to maintain state file of terraform
if aws s3 rb s3://"${bucket_name}" --force; then
    echo "S3 bucket ${bucket_name} deleted successfully"
else
    echo "Failed to delete S3 bucket ${bucket_name}"
fi

# Delete Dynamodb table that was used to maintain lock on terraform states
if aws dynamodb delete-table --table-name "${dynamo_table_name}" --region "${aws_region}"; then
    echo "DynamoDB table deleted successfully"
else
    echo "Error deleting DynamoDB table"
fi

# Delete EC2 key-pair that was used to ssh into EC2 instances
if aws ec2 delete-key-pair --key-name "${namespace}-key" --region "${aws_region}"; then
    rm "${project}-key.pem"
    echo "Key pair deleted successfully"
else
    echo "Error deleting key pair"
fi

if [[ -z "${domain}" ]]; then
    echo "Domain is null. Skipping ACM certificate deletion."
else
    certificate_arn=$(aws acm list-certificates --region "${aws_region}" --query "CertificateSummaryList[?DomainName=='${domain}'].CertificateArn" --output text)
    if [[ -z "${certificate_arn}" ]]; then
        echo "No ACM certificate found for the specified domain. Skipping ACM certificate deletion."
    else
        if aws acm delete-certificate --certificate-arn "${certificate_arn}"; then
            echo "ACM certificate deleted successfully"
        else
            echo "Failed to delete ACM certificate"
        fi
    fi
fi
