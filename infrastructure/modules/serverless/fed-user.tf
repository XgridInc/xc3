
# Creating Inline policy
resource "aws_iam_role_policy" "fed_user_policy" {
  name = "${var.namespace}-fed_user_policy"
  role = aws_iam_role.fed-user_role.id
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "Costexplorer",
        "Effect" : "Allow",
        "Action" : [
          "ce:GetCostAndUsage",
          "ce:GetCostAndUsageWithResources",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DetachNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeRegions",
          "SNS:Publish",
          "iam:ListRoles",
          "iam:ListUsers",
          "lambda:ListTags",
          "s3:PutObject",
          "s3:GetObject",
          "tag:GetResources"
        ]
         Effect   = "Allow"
        "Resource" : "*"
        
      },
     
    ]
  })
}



# Creating IAM Role for Lambda functions
resource "aws_iam_role" "fed-user_role" {
  name = "${var.namespace}-fed-user_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
    "arn:aws:iam::aws:policy/ResourceGroupsandTagEditorReadOnlyAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-fed-user_role" }))
}


data "archive_file" "fed_user_resource_zip" {
  type        = "zip"
  source_dir  = "../src/federated_user"
  output_path = "${path.module}/fed_user_resource.zip"

}


data "archive_file" "list_fed_user_zip" {
  type        = "zip"
  source_dir  = "../src/federated_user"
  output_path = "${path.module}/list_fed_user.zip"

}

resource "aws_lambda_function" "fed_user_resource" {
  #ts:skip=AC_AWS_0485 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0483 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0484 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-fed_user_resource"
  role          = aws_iam_role.fed-user_role.arn
  runtime       = "python3.9"
  handler       = "fed_user_resource.lambda_handler"
   filename      = data.archive_file.fed_user_resource_zip.output_path
  environment {
    variables = {
      prometheus_ip = "${var.prometheus_ip}:9091"
      region_names_path = "/${var.namespace}/region_names"
      bucket_name = var.s3_xc3_bucket.bucket
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  layers      = [var.prometheus_layer]
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  depends_on = [
    aws_lambda_function.list_fed_user
  ]
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-fed_user_resource" }))

}




resource "terraform_data" "list_fed_user_zip" {
  triggers_replace = [aws_lambda_function.list_fed_user.arn]
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.list_fed_user_zip.output_path}"
  }
}


resource "terraform_data" "fed_user_resource_zip" {
  triggers_replace = [aws_lambda_function.fed_user_resource.arn]
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.fed_user_resource_zip.output_path}"
  }
}


resource "aws_lambda_function" "list_fed_user" {
  #ts:skip=AC_AWS_0484 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0485 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0483 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-list_fed_users"
  role          = aws_iam_role.fed-user_role.arn
  runtime       = "python3.9"
  handler       = "list_fed_user.lambda_handler"
  filename      = data.archive_file.list_fed_user_zip.output_path
  environment {
    variables = {
      prometheus_ip = "${var.prometheus_ip}:9091"
      REGION        = var.region
      sns_topic     = var.sns_topic_arn
      bucket_name   = var.s3_xc3_bucket.bucket
      UNTAGGED_RESOURCE_LAMBDA_ARN = aws_lambda_function.untagged_resource_lambda.arn

    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  layers      = [var.prometheus_layer]
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-list_fed_user" }))
}


resource "aws_s3_object" "example_folder" {
  bucket = var.s3_xc3_bucket.bucket
  key    = "fed-resources/" 
}


resource "aws_s3_bucket_notification" "fed_user_trigger" {
  bucket = var.s3_xc3_bucket.id
  lambda_function {
    lambda_function_arn = aws_lambda_function.fed_user_resource.arn
    filter_prefix       = "fed-resources/"
    events              = ["s3:ObjectCreated:Put"]
    filter_suffix       = "resources.json"
  }
}



resource "aws_lambda_permission" "allow_buckets_for_trigger" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fed_user_resource.arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.s3_xc3_bucket.arn
}


# Grant permission to EventBridge to invoke the Lambda function
# -------------------------------------------------------------
resource "aws_lambda_permission" "allow_eventbridge_invoke" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.list_fed_user.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.federated_cron_job.arn
}