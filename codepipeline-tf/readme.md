# Terraform Module: xc3_pipeline

## Overview

This Terraform module, named `xc3_pipeline`, is designed to create and manage an AWS CodePipeline for a project. It automates the process of setting up continuous integration and continuous deployment (CI/CD) pipelines. This README provides an overview of the module, its configuration options, and how to use it.

## Module Structure

The `xc3_pipeline` module consists of the following components:

- **Source**: This module references another module named `xc3_codepipeline`, located in the `./modules/xc3_codepipeline` directory. The sub-module is responsible for defining the AWS CodePipeline resources and their configurations.

- **Input Variables**: Various input variables are provided to customize the behavior of the CodePipeline. These variables include configuration options for AWS resources, GitHub repository information, comments for approvals, and build specifications.

- **Providers**: The module specifies the required Terraform provider, in this case, the `hashicorp/aws` provider with a version constraint of `>= 5.0`.

## Configuration Options

### Tags

- `tags` (Map): A map of tags to apply to the AWS resources created by the module.

- `namespace_name` (String): A namespace identifier used within the project.

### Sensitive Values Variables

- `xc3_codepipeline_role` (String): The IAM role used to execute the CodePipeline.

- `codebuild_service_role` (String): The IAM role used to create projects for the CodePipeline.

- `codestar_connections` (String): A service role used in the CodePipeline configuration.

### GitHub Variables

- `full_repository_id` (String): The full ID of the GitHub repository.

- `full_branch_name` (String): The full name of the GitHub branch to monitor for changes.

### Comments and Description Variables

- `approve_comment_for_apply` (String): A comment to request manual approval before applying changes.

- `approve_comment_for_destroy` (String): A comment to request manual approval before destroying resources.

### Build Spec File Name Variables

- `buildspec_folder_path` (String): The path to the directory containing build specifications.

- `init_buildspec` (String): The name of the build specification for the initialization phase.

- `plan_buildspec` (String): The name of the build specification for the planning phase.

- `test_buildspec` (String): The name of the build specification for the testing phase.

- `apply_buildspec` (String): The name of the build specification for the applying phase.

- `destroy_buildspec` (String): The name of the build specification for the destroying phase.

### Compute Environment Variables

- `compute_type_for_building` (String): The type of compute environment for building.

- `os_type` (String): The operating system used in the build environment.

- `docker_image_used` (String): The Docker image used in the project.

## How to Use

To use this Terraform module, include it in your Terraform configuration, and provide values for the required variables. Here's an example of how to use it:

```hcl
module "my_codepipeline" {
  source = "./modules/xc3_pipeline"

  tags = {
    Project = "MyProject"
    Environment = "Dev"
  }

  namespace_name = "my_namespace"
  # ... Provide values for other variables ...
}
