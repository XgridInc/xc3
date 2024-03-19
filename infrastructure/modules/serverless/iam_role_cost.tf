
# Create archive file with dependencies
data "archive_file" "iam_role_cost" {
  type        = "zip"
  output_path = "${path.module}/iam_role_cost.zip"
  
  source {
    content  = file("../src/iam_roles/iam_role_cost.py")
    filename = "iam_role_cost.py"
  }
}

# Create IAM role for Lambda function
resource "aws_iam_role" "iam_role_cost" {
  name = "${var.namespace}-${var.iam_role_cost_lambda}-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

# Attach necessary policies to the IAM role
resource "aws_iam_role_policy" "iam_role_cost" {
  name   = "${var.namespace}-${var.iam_role_cost_lambda}-ce-policy"
  role   = aws_iam_role.iam_role_cost.id

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "iam:ListRoles",
        "Resource": "*"
      },
      {
        "Effect": "Allow",
        "Action": "lambda:ListFunctions",
        "Resource": "*"
      },
      {
        "Sid": "IAMroleCost",
        "Effect": "Allow",
        "Action": [
          "ce:GetCostAndUsage",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DetachNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DeleteNetworkInterface"
        ],
        "Resource": "*"
      },
      {
        "Sid": "SSMParameter",
        "Effect": "Allow",
        "Action": [
          "ssm:GetParameter"
        ],
        "Resource": "arn:aws:ssm:*:*:parameter/*"
      }, 
      {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::team1reportbucket/*"
        }
    ]
  })
}


# Create Lambda function
resource "aws_lambda_function" "iam_role_cost" {
  function_name    = "${var.namespace}-${var.iam_role_cost_lambda}"
  filename         = data.archive_file.iam_role_cost.output_path # Path to the ZIP file containing your Python code
  role             = aws_iam_role.iam_role_cost.arn
  handler          = "${var.iam_role_cost_lambda}.lambda_handler" # Assuming your handler function is named lambda_handler in lambda_function.py
  runtime          = "python3.8" # or whichever runtime your Python code requires
    environment {
      variables = {
        prometheus_ip       = "${var.prometheus_ip}:9091"
        account_detail      = var.namespace
        cur_bucket_name     = var.cur_bucket_name
        cur_file_key        = var.cur_file_key
      
      }
  }
    memory_size = var.memory_size
    timeout     = var.timeout
    layers      = [var.prometheus_layer]
    vpc_config {
      subnet_ids         = [var.subnet_id[0]]
      security_group_ids = [var.security_group_id]
    }
    tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-iam_role_cost" }))

}




