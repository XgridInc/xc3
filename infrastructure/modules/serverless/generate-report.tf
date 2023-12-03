provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

data "aws_caller_identity" "current" {}

# S3 Bucket for CUR Reports
resource "aws_s3_bucket" "cur_bucket" {
  provider = aws.us_east_1
  bucket   = "${var.namespace}-xc3-report"
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket      = aws_s3_bucket.cur_bucket.bucket
  eventbridge = true
}

resource "aws_s3_bucket_versioning" "cur_bucket_versioning" {
  provider = aws.us_east_1
  bucket   = aws_s3_bucket.cur_bucket.bucket
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Policy for specific access
resource "aws_s3_bucket_policy" "cur_bucket_policy" {
  provider = aws.us_east_1
  bucket   = aws_s3_bucket.cur_bucket.bucket
  policy = jsonencode({
    Version = "2008-10-17",
    Id      = "Policy1335892530063",
    Statement = [
      {
        Sid    = "Stmt1335892150622",
        Effect = "Allow",
        Principal = {
          Service = "billingreports.amazonaws.com"
        },
        Action = [
          "s3:GetBucketAcl",
          "s3:GetBucketPolicy"
        ],
        Resource = aws_s3_bucket.cur_bucket.arn,
        Condition = {
          StringLike = {
            "aws:SourceArn" = "arn:aws:cur:us-east-1:${data.aws_caller_identity.current.account_id}:definition/*"
          }
        }
      },
      {
        Sid    = "Stmt1335892526596",
        Effect = "Allow",
        Principal = {
          Service = "billingreports.amazonaws.com"
        },
        Action   = "s3:PutObject",
        Resource = "${aws_s3_bucket.cur_bucket.arn}/*",
        Condition = {
          StringLike = {
            "aws:SourceArn" = "arn:aws:cur:us-east-1:${data.aws_caller_identity.current.account_id}:definition/*"
          }
        }
      }
    ]
  })
}

resource "aws_cur_report_definition" "example_cur_report_definition" {
  provider = aws.us_east_1

  report_name                = "xc3report"
  time_unit                  = "DAILY"
  format                     = "textORcsv"
  compression                = "ZIP"
  additional_schema_elements = ["RESOURCES"]
  s3_bucket                  = aws_s3_bucket.cur_bucket.bucket
  s3_region                  = "us-east-1"
  s3_prefix                  = "report"
  additional_artifacts       = ["REDSHIFT", "QUICKSIGHT"]
  report_versioning          = "OVERWRITE_REPORT"
}
