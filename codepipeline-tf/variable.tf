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

################ Tags Portion ################
variable "tags" {
  description = "Tags used in this module."
  type        = map(any)
}

variable "namespace_name" {
  description = "Namespace used in project."
  type        = string
}

variable "account_id" {
  description = "AWS account ID used in module."
  type        = string
}

variable "domain_name" {
  description = "domain name used in module."
  type        = string
}

################ S3 Bucket Variables ################
variable "s3_bucket_name" {
  description = "S3 bucket varibale"
  type        = string
}

################ Senstive Values Variables ################
variable "xc3_codepipeline_role" {
  description = "This is the main role to run codepipelin."
  type        = string
}

variable "codebuild_service_role" {
  description = "This is the service role, used to create projects for codepipeline."
  type        = string
}

variable "codestar_connections" {
  description = "This is the service role, used to create projects for codepipeline."
  type        = string
}

################ Github Variables ################
variable "full_repository_id" {
  description = "Repository identity used codepipeline module."
  type        = string
}

variable "full_branch_name" {
  description = "Branch name used in codepipeline module."
  type        = string
}

################ Comments and Description Variables ################
variable "approve_comment_for_apply" {
  description = "Comment to create the XC3 infrastructure"
  type        = string
}

variable "approve_comment_for_destroy" {
  description = "Comment to destroy the XC3 infrastructure"
  type        = string
}

################ Build Spec File Name Variables ################
variable "buildspec_folder_path" {
  description = "Buildspec folder path used in codepipeline module."
  type        = string
}

variable "init_buildspec" {
  description = "Initialize and validate terraform configuration file variable"
  type        = string
}

variable "plan_buildspec" {
  description = "Plan run of XC3 infrastructure file variable"
  type        = string
}

variable "test_buildspec" {
  description = "Unit testing file variable"
  type        = string
}

variable "apply_buildspec" {
  description = "Create XC3 infrastructure file variable"
  type        = string
}

variable "destroy_buildspec" {
  description = "Destroy XC3 infrastructure file variable"
  type        = string
}

################ Compute Environment Variables ################
variable "compute_type_for_building" {
  description = "Build environment compute type variable."
  type        = string
}

variable "os_type" {
  description = "Operating system variable."
  type        = string
}

variable "docker_image_used" {
  description = "Docker image used in project variable."
  type        = string
}

variable "region" {
  description = "Region used for pipeline testing."
  type        = string
}

variable "key" {
  description = "key used in codepipeline(state file key)."
  type        = string
}
