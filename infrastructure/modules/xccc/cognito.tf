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

resource "aws_cognito_user_pool" "grafana_pool" {
  name = "${var.namespace}-grafana-userpool"

  username_configuration {
    case_sensitive = true
  }

  alias_attributes = ["email", "preferred_username"]


  schema {
    attribute_data_type = "String"
    name                = "name"
    required            = true
    mutable             = true
  }

  lifecycle {
    ignore_changes = [schema]
  }

  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 7
  }

  verification_message_template {
    email_message = "Please click the link below to verify your email address: {####}"
    email_subject = "Verify your email address"
  }


  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  /* Uncomment the next line to enable self-service account recovery */
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-Grafana-User-Pool" }))
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = var.cognito_domain
  user_pool_id = aws_cognito_user_pool.grafana_pool.id
}

resource "aws_cognito_user_pool_client" "grafana_client" {
  name                                 = "${var.namespace}-grafana-client"
  user_pool_id                         = aws_cognito_user_pool.grafana_pool.id
  supported_identity_providers         = ["COGNITO"]
  allowed_oauth_flows_user_pool_client = true
  access_token_validity                = 60
  id_token_validity                    = 60

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  generate_secret      = true
  allowed_oauth_flows  = ["code"]
  allowed_oauth_scopes = ["email", "openid", "aws.cognito.signin.user.admin", "profile"]

  callback_urls = ["https://${var.domain_name}/generic_oauth", "https://${var.domain_name}/login", "https://${var.domain_name}/login/generic_oauth"]
  logout_urls   = ["https://${var.domain_name}/login"]

  explicit_auth_flows = ["ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_PASSWORD_AUTH"]

  prevent_user_existence_errors = "ENABLED"
}

resource "aws_cognito_user_group" "admin_group" {
  name         = "Admin"
  description  = "Authentication Group"
  user_pool_id = aws_cognito_user_pool.grafana_pool.id
}
