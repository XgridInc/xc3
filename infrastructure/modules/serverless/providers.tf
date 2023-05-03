terraform {
  required_version = ">= 1.0"

  required_providers {
    null = {
      source  = "hashicorp/null"
      version = ">= 3.0.0"
    }
  }
}

resource "null_resource" "upload_files_on_s3" {
  triggers = {
    s3_bucket = var.s3_xccc_bucket.arn
  }

  provisioner "local-exec" {
    command = <<EOT
    aws s3 cp python.zip s3://${var.s3_xccc_bucket.id}/apprise/ ||
    echo "Failed to upload files to S3"
   EOT
  }
}
