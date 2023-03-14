data "aws_ssm_parameter" "dbusername" {
  name = "/${var.namespace}/dbusername"
}

data "aws_ssm_parameter" "database" {
  name = "/${var.namespace}/database"
}

data "aws_ssm_parameter" "dbpassword" {
  name = "/${var.namespace}/dbpassword"
}
