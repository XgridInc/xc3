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
##################################################
# tfvars
##################################################


namespace_name = "example"
account_id     = "your-account-id"
domain_name    = "your-domain"
region         = "eu-west-1"

s3_bucket_name = "terraform-state-xc3-example-pipeline"

//delete after deployment
key = "xc3\\/xc3.tfstate"

xc3_codepipeline_role = "example-pipeline-role"
codebuild_service_role = "codebuild-example-service"
codestar_connections   = "code-star-connection-role"

approve_comment_for_apply   = "This approval needs to create XC3 infrastructure."
approve_comment_for_destroy = "This approval needs to destroy XC3 infrastructure."

full_repository_id = "your full repo id"
full_branch_name   = "main"

buildspec_folder_path = "./buildspec_yml/"
init_buildspec        = "init_buildspec.yml"
plan_buildspec        = "plan_buildspec.yml"
test_buildspec        = "unit_test_buildspec.yml"
apply_buildspec       = "apply_buildspec.yml"
destroy_buildspec     = "destroy_buildspec.yml"

compute_type_for_building = "BUILD_GENERAL1_SMALL"
os_type                   = "LINUX_CONTAINER"
docker_image_used         = "hashicorp/terraform:latest"


tags = {
  app         = "Codepipeline",
  created-by  = "Terraform",
  environment = "dev",
  name        = "example",
  project     = "test",
  owner       = "example@example.co",
  creator     = "example@example.co",
  team        = "team"
}
