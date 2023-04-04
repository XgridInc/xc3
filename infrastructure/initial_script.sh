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

aws_region="eu-west-1"
dynamo_table_name="terraform-lock"
bucket_name="terraform-state-xccc"
namespace="x-ccc"
domain="xccc.xgrid.co"

aws s3api create-bucket --bucket ${bucket_name} --region ${aws_region} --create-bucket-configuration LocationConstraint=${aws_region}
aws s3api put-bucket-versioning --bucket ${bucket_name} --versioning-configuration Status=Enabled --region ${aws_region}
aws s3api put-bucket-encryption \
	--bucket ${bucket_name} \
	--server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}' --region ${aws_region}

aws s3api put-public-access-block --bucket ${bucket_name} --region ${aws_region} \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

aws dynamodb create-table \
    --table-name ${dynamo_table_name} \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
    --tags Key=backup,Value=short



aws ec2 create-key-pair --key-name ${namespace}-key --tag-specifications \
 "ResourceType=key-pair,Tags=[{Key=Project,Value=${namespace}},{Key=Owner,Value=xccc@xgrid.co},{Key=Creator,Value=saman.batool@xgrid.co}]" \
    --query 'KeyMaterial' --output text > ${namespace}-key.pem --region=eu-west-1

aws acm request-certificate \
    --domain-name ${domain} \
    --validation-method DNS \
    --key-algorithm RSA_2048 \
    --region ${aws_region} \
    --tags '[{"Key:"Project","Value":"x-ccc"}, {"Key":"Owner","Value":"xccc@xgrid.co"}, {"Key":"Creator","Value":"saman.batool@xgrid.co"}]'
