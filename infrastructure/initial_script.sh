#!/usr/bin/env bash

aws_region="eu-west-1"
dynamo_table_name="terraform-lock"
bucket_name="terraform-state-xccc"

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
    