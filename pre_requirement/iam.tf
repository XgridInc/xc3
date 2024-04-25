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
locals {
  tags = {
    Owner   = var.owner_email
    Creator = var.creator_email
    Project = var.project
  }
}

resource "aws_iam_role" "this" {
  name = "${var.namespace}-infra_access_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonRoute53ReadOnlyAccess",
    "arn:aws:iam::aws:policy/ResourceGroupsandTagEditorReadOnlyAccess",
    "arn:aws:iam::aws:policy/CloudWatchEventsReadOnlyAccess",
    "arn:aws:iam::aws:policy/AWSCloudTrail_ReadOnlyAccess"
  ]
  # Attach inline policy
  dynamic "inline_policy" {
    for_each = var.iam_permission_policies
    content {
      name   = "${var.namespace}-${inline_policy.key}-terraform_permission_set_policy"
      policy = file(inline_policy.value)
    }
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-infrastructure-role" }))

}
