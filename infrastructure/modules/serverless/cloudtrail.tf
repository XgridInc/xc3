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

resource "aws_kms_alias" "this" {
  name          = "alias/${var.namespace}-kms-key"
  target_key_id = aws_kms_key.this.key_id
}

#Create a KMS Key for CloudTrail encryption
resource "aws_kms_key" "this" {
  description         = "KMS key for CloudTrail encryption"
  enable_key_rotation = true
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        },
        Action   = "kms:*",
        Resource = "*"
      },
      {
        Sid    = "Allow CloudTrail to encrypt logs"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action = [
          "kms:GenerateDataKey",
          "kms:Decrypt"
        ]
        Resource = "*"
      }
    ]
  })
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-kms-key" }))

}

# Create an S3 bucket for storing CloudTrail logs
resource "aws_s3_bucket" "this" {
  #ts:skip=AWS.S3Bucket.LM.MEDIUM.0078 We are aware of the risk and choose to skip this rule
  bucket = "${var.namespace}-cloudtrail-logs-storage"
  tags   = merge(local.tags, tomap({ "Name" = "${var.namespace}-bucket" }))

}

resource "aws_s3_bucket_acl" "this" {
  bucket = aws_s3_bucket.this.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "bucket_versioning" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_policy" "this" {
  bucket = aws_s3_bucket.this.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = "arn:aws:s3:::${aws_s3_bucket.this.id}"
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "arn:aws:s3:::${aws_s3_bucket.this.id}/cloudtrail/*/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# Create a CloudTrail trail and enable logging to the S3 bucket
resource "aws_cloudtrail" "this" {
  depends_on                    = [aws_s3_bucket_policy.this]
  name                          = "${var.namespace}-cloudtrail"
  s3_bucket_name                = aws_s3_bucket.this.id
  s3_key_prefix                 = "cloudtrail"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  kms_key_id                    = aws_kms_key.this.arn
  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-cloudtrail" }))

}
