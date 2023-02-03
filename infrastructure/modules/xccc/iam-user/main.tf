
module "lambda_function_s3_trigger_sns" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "lambda_function_s3_trigger_sns"
  description   = "Lambda function triggered by changes to an S3 bucket and publishes a message to an SNS topic"
  handler       = "index.handler"
  runtime       = "nodejs12.x"

  filename = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")

  environment = {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.sns_topic.arn
    }
  }

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }

  vpc_config = {
    subnet_ids         = [aws_subnet.private.*.id[0], aws_subnet.private.*.id[1]]
    security_group_ids = [aws_security_group.lambda.id]
  }

  depends_on = [
    aws_sns_topic_subscription.sns_subscription
  ]
}

resource "aws_sns_topic" "sns_topic" {
  name = "lambda_function_sns_topic"
}

resource "aws_sns_topic_subscription" "sns_subscription" {
  topic_arn = aws_sns_topic.sns_topic.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function_s3_trigger_sns.arn
}

resource "aws_s3_bucket" "bucket" {
  bucket = "lambda_function_s3_bucket"
}

resource "aws_lambda_permission" "lambda_permission_s3" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function_s3_trigger_sns.function_arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket.arn
}

resource "aws_s3_bucket_notification_configuration" "bucket_notification" {
  bucket = aws_s3_bucket.bucket.id

  lambda_function_configurations = [
    {
      lambda_function_arn = module.lambda_function_s3_trigger_sns.arn
      events              = ["s3:ObjectCreated:*"]
    },
  ]
}
