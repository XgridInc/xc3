terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"

    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.0.0"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.0.0"
    }
  }
}

resource "terraform_data" "upload_files_on_s3" {
  triggers_replace = [var.s3_xc3_bucket.arn]

  provisioner "local-exec" {
    command = <<EOT
    aws s3 cp python.zip s3://${var.s3_xc3_bucket.id}/apprise/ ||
    echo "Failed to upload files to S3"
   EOT
  }
}
