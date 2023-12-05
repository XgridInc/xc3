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

# Create an S3 bucket for storing CloudTrail logs
resource "aws_s3_bucket" "this" {
  #ts:skip=AWS.S3Bucket.IAM.High.0370 We are aware of the risk and choose to skip this rule
  count = var.create_cloudtrail_s3_bucket ? 1 : 0
  bucket = "${var.namespace}-cloudtrail-logs-storage"
  tags   = merge(local.tags, tomap({ "Name" = "${var.namespace}-bucket" }))
}

resource "aws_s3_bucket_versioning" "this" {
  count = var.create_cloudtrail_s3_bucket ? 1 : 0
  bucket = aws_s3_bucket.this[count.index].id
  versioning_configuration {
    status = "Enabled"
  }
}

# Create a CloudTrail trail and enable logging to the S3 bucket
resource "aws_cloudtrail" "this" {
  count = var.create_cloudtrail ? 1 : 0

  depends_on                    = [aws_s3_bucket.this]
  name                          = "${var.namespace}-cloudtrail"
  s3_bucket_name                = var.create_cloudtrail_s3_bucket ? aws_s3_bucket.this[0].id : null
  s3_key_prefix                 = "cloudtrail"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  kms_key_id                    = var.create_cloudtrail_kms ? aws_kms_key.this[0].arn : null

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-cloudtrail" }))
}

resource "aws_s3_bucket_policy" "this" {
  count  = var.create_cloudtrail_kms && var.create_cloudtrail_s3_bucket ? 1 : 0
  bucket = var.create_cloudtrail_s3_bucket ? aws_s3_bucket.this[0].id : null

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "AWSCloudTrailAclCheck",
        Effect    = "Allow",
        Principal = { Service = "cloudtrail.amazonaws.com" },
        Action    = "s3:GetBucketAcl",
        Resource  = var.create_cloudtrail_s3_bucket ? "arn:aws:s3:::${aws_s3_bucket.this[0].id}" : null
      },
      {
        Sid       = "AWSCloudTrailWrite",
        Effect    = "Allow",
        Principal = { Service = "cloudtrail.amazonaws.com" },
        Action    = "s3:PutObject",
        Resource  = var.create_cloudtrail_s3_bucket ? "arn:aws:s3:::${aws_s3_bucket.this[0].id}/cloudtrail/*/*" : null,
        Condition = var.create_cloudtrail_s3_bucket ? {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        } : null
      }
    ]
  })
}

# Create a KMS key for CloudTrail encryption
resource "aws_kms_key" "this" {
  #ts:skip=AWS.AKK.IAM.HIGH.0082 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.AKK.DP.HIGH.0012 We are aware of the risk and choose to skip this rule
  count = var.create_cloudtrail_kms ? 1 : 0

  description             = "KMS key for CloudTrail"
  deletion_window_in_days = 7
  tags                    = merge(local.tags, tomap({ "Name" = "${var.namespace}-kms" }))

  policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "Enable IAM User Permissions",
        "Effect": "Allow",
        "Principal": {
          "AWS": "*"
        },
        "Action": "kms:*",
        "Resource": "*"
      },
      {
        "Sid": "Allow CloudTrail to encrypt logs",
        "Effect": "Allow",
        "Principal": {
          "Service": "cloudtrail.amazonaws.com"
        },
        "Action": [
          "kms:GenerateDataKey",
          "kms:Decrypt"
        ],
        "Resource": "*"
      }
    ]
  }
EOF
}

resource "aws_kms_alias" "create_cloudtrail_kms_alias" {
    count = var.env != "prod" && var.create_cloudtrail_kms && length(data.aws_kms_alias.check_existing_kms) == 0 ? 1 : 0

  name          = var.create_cloudtrail_kms ? "alias/${var.namespace}-kms-key" : null
  target_key_id = var.create_cloudtrail_kms ? aws_kms_key.this[0].key_id : null
}
