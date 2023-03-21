locals {
  tags_label = {
    Owner   = var.owner_email
    Creator = var.creator_email
    Project = var.namespace
  }
}

resource "aws_kms_alias" "this" {
  name          = "${var.namespace}-kms-key"
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
        }
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
  tags = merge(local.tags_label, tomap({ "Name" = "${local.tags_label.Project}-kms-key" }))

}

# Create an S3 bucket for storing CloudTrail logs
resource "aws_s3_bucket" "this" {
  bucket = "${var.namespace}-cloudtrail-logs-storage"
  tags   = merge(local.tags_label, tomap({ "Name" = "${local.tags_label.Project}-bucket" }))

}

resource "aws_s3_bucket_acl" "this" {
  bucket = aws_s3_bucket.this.id
  acl    = "private"
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
  tags = merge(local.tags_label, tomap({ "Name" = "${local.tags_label.Project}-cloudtrail" }))

}
