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

# code pipeline module
module "xc3_pipeline" {

  source = "./modules/xc3_codepipeline"
  tags = var.tags
  
  namespace_name              = var.namespace_name
  account_id                  = var.account_id
  domain_name                 = var.domain_name
  xc3_codepipeline_role       = var.xc3_codepipeline_role
  codebuild_service_role      = var.codebuild_service_role
  codestar_connections        = var.codestar_connections
  approve_comment_for_apply   = var.approve_comment_for_apply
  approve_comment_for_destroy = var.approve_comment_for_destroy
  buildspec_folder_path       = var.buildspec_folder_path
  init_buildspec              = var.init_buildspec
  plan_buildspec              = var.plan_buildspec
  test_buildspec              = var.test_buildspec
  apply_buildspec             = var.apply_buildspec
  destroy_buildspec           = var.destroy_buildspec
  compute_type_for_building   = var.compute_type_for_building
  os_type                     = var.os_type
  docker_image_used           = var.docker_image_used
  s3_bucket_name              = var.s3_bucket_name
  full_repository_id          = var.full_repository_id
  full_branch_name            = var.full_branch_name
  region = var.region
  key = var.key
}
