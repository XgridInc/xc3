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

data "archive_file" "lambda_function_zip" {
  type        = "zip"
  for_each    = var.lambda_names
  source_file = each.value
  output_path = "${path.module}/${each.key}.zip"
}

resource "aws_lambda_function" "IamRolestoGrafana" {
  #ts:skip=AC_AWS_0483 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0485 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0484 We are aware of the risk and choose to skip this rule

  function_name = "${var.namespace}-iamrolestografana"
  role          = aws_iam_role.lambda_execution_role_IamRolestoGrafana.arn
  runtime       = "python3.9"
  handler       = "iam_roles_all.lambda_handler"
  filename      = values(data.archive_file.lambda_function_zip)[0].output_path

  environment {
    variables = {
      func_name_iam_role_service_mapping = aws_lambda_function.IamRolesServiceMapping.arn
      prometheus_ip                      = "${var.prometheus_ip}:9091"
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }

  layers = [var.prometheus_layer]

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-iam_roles_to_grafana" }))

}

resource "aws_iam_role_policy" "IamRolestoGrafana" {
  name = "${var.namespace}-iamrolestografana-lambda-inline-policy"
  role = aws_iam_role.lambda_execution_role_IamRolestoGrafana.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Effect" : "Allow",
        "Action" : [
          "lambda:InvokeFunction"
        ],
        "Resource" : [
          aws_lambda_function.IamRolesServiceMapping.arn
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:GetObject"
        ],
        "Resource" : [
          "arn:aws:s3:::${var.s3_xc3_bucket.id}/*"
        ]
      }
    ]
  })
}

# Creating IAM Role for Lambda functions
resource "aws_iam_role" "lambda_execution_role_IamRolestoGrafana" {
  name = "${var.namespace}-iamrolestografana"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "iamrolestografanarole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess", "arn:aws:iam::aws:policy/ResourceGroupsandTagEditorReadOnlyAccess", "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-IAM-Role-to-Grafana" }))
}

resource "aws_lambda_function" "IamRolesServiceMapping" {
  #ts:skip=AC_AWS_0483 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0485 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0484 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-iamrolesservicemapping"
  role          = aws_iam_role.lambda_execution_role_IamRolesServiceMapping.arn
  runtime       = "python3.9"
  handler       = "iamrolesservicemapping.lambda_handler"
  filename      = values(data.archive_file.lambda_function_zip)[2].output_path

  environment {
    variables = {
      function_name_iamroleservice = aws_lambda_function.IamRolesService.arn
    }
  }

  memory_size = var.memory_size
  timeout     = var.timeout
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-iamroleservicemapping" }))

}

# Creating IAM Role for Lambda functions
resource "aws_iam_role" "lambda_execution_role_IamRolesServiceMapping" {
  name = "${var.namespace}-iamrolesservicemapping"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "iamrolesservicemappingrole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess", "arn:aws:iam::aws:policy/ResourceGroupsandTagEditorReadOnlyAccess", "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-IAM-Role-Service-Mapping" }))
}

resource "aws_iam_role_policy" "IamRolesServiceMapping" {
  name = "${var.namespace}-iamrolesservicemapping-lambda-inline-policy"
  role = aws_iam_role.lambda_execution_role_IamRolesServiceMapping.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Effect" : "Allow",
        "Action" : [
          "lambda:InvokeFunction"
        ],
        "Resource" : [
          aws_lambda_function.IamRolesService.arn
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "iam:ListInstanceProfilesForRole",
          "iam:PassRole"
        ],
        "Resource" : ["*"]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "ec2:DescribeInstances",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AttachNetworkInterface"
        ],
        "Resource" : "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_xc3_bucket.id}/*"
        ]
      }
    ]
  })
}


resource "aws_lambda_function" "IamRolesService" {
  #ts:skip=AC_AWS_0483 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0485 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0484 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-iamrolesservice"
  role          = aws_iam_role.lambda_execution_role_IamRolesService.arn
  runtime       = "python3.9"
  handler       = "iamrolesservice.lambda_handler"
  filename      = values(data.archive_file.lambda_function_zip)[1].output_path
  environment {
    variables = {
      prometheus_ip = "${var.prometheus_ip}:9091"
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }

  layers = [var.prometheus_layer]

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-iamroleservice" }))

}

resource "aws_iam_role_policy" "IamRolesService" {
  name = "${var.namespace}-iamrolesservice-lambda-inline-policy"
  role = aws_iam_role.lambda_execution_role_IamRolesService.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Effect" : "Allow",
        "Action" : [
          "ce:GetCostAndUsageWithResources"
        ],
        "Resource" : "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "lambda:InvokeFunction"
        ],
        "Resource" : [
          aws_lambda_function.IamRolesService.arn
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "ec2:DescribeInstances",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AttachNetworkInterface"
        ],
        "Resource" : "*"
      }
    ]
  })
}

# Creating IAM Role for Lambda functions
resource "aws_iam_role" "lambda_execution_role_IamRolesService" {
  name = "${var.namespace}-iamrolesservice"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "iamrolesservicerole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess", "arn:aws:iam::aws:policy/ResourceGroupsandTagEditorReadOnlyAccess", "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-IAM-Role-Service" }))
}

resource "aws_lambda_function" "InstanceChangeState" {
  #ts:skip=AC_AWS_0485 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0484 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-instancestatechange"
  role          = aws_iam_role.lambda_execution_role_InstanceChangeState.arn
  runtime       = "python3.9"
  handler       = "instancestatechange.lambda_handler"
  filename      = values(data.archive_file.lambda_function_zip)[3].output_path

  memory_size = var.memory_size
  timeout     = var.timeout
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }

  layers = [var.prometheus_layer]

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-instancestatechange" }))

}

resource "aws_iam_role_policy" "InstanceChangeState" {
  name = "${var.namespace}-instancestatechange-lambda-inline-policy"
  role = aws_iam_role.lambda_execution_role_InstanceChangeState.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Sid" : "StartStopEC2",
        "Effect" : "Allow",
        "Action" : [
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeInstances",
          "ec2:AttachNetworkInterface"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "lambda:InvokeFunction"
        ],
        "Resource" : [
          aws_lambda_function.InstanceChangeState.arn
        ]
      },
      {
        "Sid" : "AllowAPIGatewayUpdate",
        "Effect" : "Allow",
        "Action" : [
          "apigateway:UpdateRestApiPolicy",
          "apigateway:PATCH",
          "apigateway:GET",
          "apigateway:POST"
        ],
        "Resource" : [aws_api_gateway_rest_api.apiLambda.arn]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Creating IAM Role for Lambda functions
resource "aws_iam_role" "lambda_execution_role_InstanceChangeState" {
  name = "${var.namespace}-instancestatechange"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "instancestatechangerole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess", "arn:aws:iam::aws:policy/ResourceGroupsandTagEditorReadOnlyAccess", "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-instance-state-change" }))
}

resource "aws_lambda_permission" "allow_bucket_for_irtg" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.IamRolestoGrafana.arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.s3_xc3_bucket.arn
}

resource "aws_s3_bucket_notification" "IamRolestoGrafana_trigger" {
  bucket = var.s3_xc3_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.IamRolestoGrafana.arn
    filter_prefix       = "iam-role-all/"
    events              = ["s3:ObjectCreated:Put"]
    filter_suffix       = "resources.json.gz"
  }
}

resource "aws_api_gateway_rest_api" "apiLambda" {
  name = "instance-state-change"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  parent_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
  path_part   = "cost-details"
}

resource "aws_api_gateway_method" "proxyMethod" {
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "POST"
  authorization = "AWS_IAM"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  resource_id = aws_api_gateway_method.proxyMethod.resource_id
  http_method = aws_api_gateway_method.proxyMethod.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.InstanceChangeState.invoke_arn
}




resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  resource_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
  http_method   = "POST"
  authorization = "AWS_IAM"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  resource_id = aws_api_gateway_method.proxy_root.resource_id
  http_method = aws_api_gateway_method.proxy_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.InstanceChangeState.invoke_arn
}


resource "aws_api_gateway_deployment" "apideploy" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root,
  ]

  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  stage_name  = "deploy"
}


resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.InstanceChangeState.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.apiLambda.execution_arn}/*/*"
}

resource "terraform_data" "delete_zips" {
  for_each         = var.lambda_names
  triggers_replace = ["arn:aws:lambda:${var.region}:${var.account_id}:function:${each.key}"]

  depends_on = [aws_lambda_function.IamRolesService, aws_lambda_function.InstanceChangeState, aws_lambda_function.IamRolesServiceMapping,
  aws_lambda_function.IamRolestoGrafana]

  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.lambda_function_zip[each.key].output_path}"
  }

}
