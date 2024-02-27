/*
Copyright (c) 2023, Xgrid Inc, https://xgrid.co

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
*/

resource "aws_iam_policy" "codebuild_service_policy_FH" {
  name = "xc3_codebuild_service_role_FH"

  # Adjust policy document as needed
  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Sid       = "VisualEditor0",
        Effect    = "Allow",
        Action    = [
          "sqs:*",
          "lambda:*",
          "iam:*",
          "ssm:*",
          "codedeploy:*",
          "sns:*",
          "codestar:*",
          "logs:*",
          "events:*",
          "codebuild:*",
          "dynamodb:*",
          "ses:*",
          "sts:*",
          "organizations:*",
          "ce:*",
          "aws-portal:*",
          "apigateway:*",
          "s3:*",
          "elasticloadbalancing:*",
          "acm:*",
          "kms:*",
          "route53:*",
          "cognito-idp:*",
          "cloudtrail:*",
          "codestar-connections:*",
          "ec2:*",
          "opsworks:*",
          "cloudwatch:*",
          "wafv2:*"
        ],
        Resource  = "*"
      },
      {
        Sid       = "KMSPermissions",
        Effect    = "Allow",
        Action    = [
          "kms:ListAliases"
        ],
        Resource  = "*"
      },
      {
        Sid       = "EC2Permissions",
        Effect    = "Allow",
        Action    = [
          "ec2:DescribeImages",
          "ec2:DescribeKeyPairs"
        ],
        Resource  = "*"
      },
      {
        Sid       = "ACMPermissions",
        Effect    = "Allow",
        Action    = [
          "acm:ListCertificates"
        ],
        Resource  = "*"
      }
    ]
  })
}


# IAM Role for CodeBuild service role
resource "aws_iam_role" "codebuild_service_role" {
  name               = var.codebuild_service_role
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })
}

# Attach IAM policy to CodeBuild service role
resource "aws_iam_policy_attachment" "codebuild_service_policy_attachment_FH" {
  name       = "xc3_codebuild_service_policy_attachment_FH"
  policy_arn = aws_iam_policy.codebuild_service_policy_FH.arn
  roles      = [aws_iam_role.codebuild_service_role.name]
}

# Attach managed policy to CodeBuild service role
resource "aws_iam_policy_attachment" "codebuild_managed_policy_attachment" {
  name       = "xc3_codebuild_test_managed_policy_attachment"
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
  roles      = [aws_iam_role.codebuild_service_role.name]
}

# IAM Policy for pipeline role
resource "aws_iam_policy" "xc3_pipeline_policy" {
  name = "xc3_pipeline_policy"

  # Adjust policy document as needed
  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Sid       = "VisualEditor0",
        Effect    = "Allow",
        Action    = [
          "codedeploy:*",
          "sns:*",
          "codestar:*",
          "logs:*",
          "events:*",
          "codebuild:*",
          "dynamodb:*",
          "s3:*",
          "codestar-connections:*",
          "codepipeline:*"
        ],
        Resource  = "*"
      }
    ]
  })
}

# IAM Role for pipeline role
resource "aws_iam_role" "xc3_pipeline_role" {
  name               = var.xc3_codepipeline_role
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = [
            "codedeploy.amazonaws.com",
            "codepipeline.amazonaws.com"
          ]
        }
      }
    ]
  })
}

# Attach IAM policy to pipeline role
resource "aws_iam_policy_attachment" "xc3_pipeline_policy_attachment" {
  name       = "xc3_pipeline_policy_attachment"
  policy_arn = aws_iam_policy.xc3_pipeline_policy.arn
  roles      = [aws_iam_role.xc3_pipeline_role.name]
}

# Attach managed policy to pipeline role
resource "aws_iam_policy_attachment" "xc3_pipeline_managed_policy_attachment" {
  name       = "xc3_pipeline_managed_policy_attachment"
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeDeployDeployerAccess"
  roles      = [aws_iam_role.xc3_pipeline_role.name]
}

#creating S3 bucket
resource "aws_s3_bucket" "this" {
  bucket        = var.s3_bucket_name
  force_destroy = true
  tags = var.tags
}
resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}


# codepipeline main resource
resource "aws_codepipeline" "this" {
  name     = "${var.tags.app}-${var.tags.environment}-tf-pipeline"
  role_arn = aws_iam_role.xc3_pipeline_role.arn
  artifact_store {
    location = aws_s3_bucket.this.bucket
    type     = "S3"
  }

  stage {
    name = "Source_Stage"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["xc3_infra_code"]

      configuration = {
        ConnectionArn    = var.codestar_connections
        FullRepositoryId = var.full_repository_id
        BranchName       = var.full_branch_name
      }
    }
  }

  stage {
    name = "Terraform_Init_Stage"

    action {
      name             = "Init_and_Validate"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["xc3_infra_code"]
      output_artifacts = ["xc3_infra_init"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.codebuild_project_init_stage.name
      }
    }
  }
  stage {
    name = "Terraform_Plan_Stage"

    action {
      name             = "Plan"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["xc3_infra_init"]
      output_artifacts = ["xc3_infra_plan"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.codebuild_project_plan_stage.name
      }
    }
  }
  stage {
    name = "Terraform_Testing_Stage"

    action {
      name             = "Testing"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["xc3_infra_plan"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.codebuild_project_test_stage.name
      }
    }
  }
  stage {
    name = "Manual_Approval_for_Apply"

    action {
      name     = "Approval"
      category = "Approval"
      owner    = "AWS"
      provider = "Manual"
      version  = "1"

      configuration = {
        CustomData = var.approve_comment_for_apply
      }
    }
  }
  stage {
    name = "Terraform_Apply_Stage"

    action {
      name             = "Deploy"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["xc3_infra_plan"]
      output_artifacts = ["xc3_infra_deploy"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.codebuild_project_apply_stage.name
      }
    }
  }
  stage {
    name = "Approval_for_Destroy"

    action {
      name     = "Destroy_XC3_Infra"
      category = "Approval"
      owner    = "AWS"
      provider = "Manual"
      version  = "1"

      configuration = {
        CustomData = var.approve_comment_for_destroy
      }
    }
  }
  stage {
    name = "Destroy"

    action {
      name            = "Destroy"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["xc3_infra_deploy"]
      version = "1"

      configuration = {
        ProjectName = aws_codebuild_project.codebuild_project_destroy_stage.name
      }
    }
  }

  tags = var.tags
}

#####################################################################################################################################################
### Projects resources
#stage 1
resource "aws_codebuild_project" "codebuild_project_init_stage" {
  name         = "${var.tags.app}-${var.tags.environment}-init-project"
  description  = "Terraform Init and Validate Stage for infra XC3"
  service_role = aws_iam_role.codebuild_service_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type = var.compute_type_for_building
    type         = var.os_type
    image        = var.docker_image_used
        environment_variable {
            name  = "namespace"
            value = var.namespace_name
        }
        environment_variable {
            name  = "account_id"
            value = var.account_id
        }
        environment_variable {
            name  = "domain_name"
            value = var.domain_name
        }
        environment_variable {
            name  = "s3_bucket_name"
            value = var.s3_bucket_name
        }
        environment_variable {
            name  = "key"
            value = var.key
        }
  }
  
  source {
    type      = "CODEPIPELINE"
    buildspec = file("${var.buildspec_folder_path}${var.init_buildspec}")
  }
}
#stage 2
resource "aws_codebuild_project" "codebuild_project_plan_stage" {
  name         = "${var.tags.app}_${var.tags.environment}-plan-project"
  description  = "Terraform Plan Stage for infra XC3"
  service_role = aws_iam_role.codebuild_service_role.arn


  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type = var.compute_type_for_building
    type         = var.os_type
    image        = var.docker_image_used
        environment_variable {
            name  = "namespace"
            value = var.namespace_name
        }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = file("${var.buildspec_folder_path}${var.plan_buildspec}")
  }
}
#stage unit test
resource "aws_codebuild_project" "codebuild_project_test_stage" {
  name         = "${var.tags.app}-${var.tags.environment}-test-project"
  description  = "Terraform Test Stage for infra XC3"
  service_role = aws_iam_role.codebuild_service_role.arn


  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type = var.compute_type_for_building
    type         = var.os_type
    image        = var.docker_image_used
        environment_variable {
            name  = "namespace"
            value = var.namespace_name
        }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = file("${var.buildspec_folder_path}${var.test_buildspec}")
  }
}
#stage 3
resource "aws_codebuild_project" "codebuild_project_apply_stage" {
  name         = "${var.tags.app}-${var.tags.environment}-apply-project"
  description  = "Terraform Apply Stage for infra XC3"
  service_role = aws_iam_role.codebuild_service_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type = var.compute_type_for_building
    type         = var.os_type
    image        = var.docker_image_used
        environment_variable {
            name  = "namespace"
            value = var.namespace_name
        }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = file("${var.buildspec_folder_path}${var.apply_buildspec}")
  }
}
#stage 4
resource "aws_codebuild_project" "codebuild_project_destroy_stage" {
  name         = "${var.tags.app}-${var.tags.environment}-destroy-project"
  description  = "Terraform Apply Stage for infra XC3"
  service_role = aws_iam_role.codebuild_service_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type = var.compute_type_for_building
    type         = var.os_type
    image        = var.docker_image_used
        environment_variable {
            name  = "namespace"
            value = var.namespace_name
        }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = file("${var.buildspec_folder_path}${var.destroy_buildspec}")
  }
}
