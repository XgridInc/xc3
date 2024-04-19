provider "aws" {
  alias  = "west"
  region = var.region
}

data "aws_caller_identity" "current" {}

# Define an S3 bucket policy to grant permissions for AWS Cost 
# and Usage Report service to access the bucket.
resource "aws_s3_bucket_policy" "cur_bucket_policy" {
  bucket = var.s3_xc3_bucket.bucket
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
        Resource = var.s3_xc3_bucket.arn,
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
        Resource = "${var.s3_xc3_bucket.arn}/*",
        Condition = {
          StringLike = {
            "aws:SourceArn" = "arn:aws:cur:us-east-1:${data.aws_caller_identity.current.account_id}:definition/*"
          }
        }
      }
    ]
  })
}

resource "aws_cur_report_definition" "example_cur" {
  #it's a configuration setting that defines how AWS generates and delivers your cost and usage reports.
  provider = aws.west

  report_name                = "xc3report"
  time_unit                  = "DAILY"
  format                     = "textORcsv"
  compression                = "ZIP"
  additional_schema_elements = ["RESOURCES"]
  s3_bucket                  = var.s3_xc3_bucket.bucket
  s3_region                  = var.region
  s3_prefix                  = "report"
  additional_artifacts       = ["REDSHIFT", "QUICKSIGHT"]
  report_versioning          = "OVERWRITE_REPORT"
}
