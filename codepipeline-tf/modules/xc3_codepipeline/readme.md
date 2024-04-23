# Terraform CodePipeline Module

This Terraform module sets up a continuous integration and continuous deployment (CI/CD) pipeline using AWS CodePipeline and AWS CodeBuild.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Usage](#usage)
  - [Inputs](#inputs)
  - [Outputs](#outputs)
- [Example](#example)
- [License](#license)

## Prerequisites

Before using this module, ensure you have:

- An AWS account
- Terraform installed locally
- Basic knowledge of AWS services like CodePipeline, CodeBuild, IAM, and S3

## Usage

To use this module, follow these steps:

1. **Module Installation**: Include this module in your Terraform configuration files.

```hcl
module "codepipeline" {
  source = "git::https://github.com/your-repo/path-to-module"

  # Input variables
  tags                         = var.tags
  namespace_name               = var.namespace_name
  account_id                   = var.account_id
  domain_name                  = var.domain_name
  s3_bucket_name               = var.s3_bucket_name
  xc3_codepipeline_role        = var.xc3_codepipeline_role
  codebuild_service_role       = var.codebuild_service_role
  codestar_connections         = var.codestar_connections
  full_repository_id           = var.full_repository_id
  full_branch_name             = var.full_branch_name
  approve_comment_for_apply    = var.approve_comment_for_apply
  approve_comment_for_destroy  = var.approve_comment_for_destroy
  buildspec_folder_path        = var.buildspec_folder_path
  init_buildspec               = var.init_buildspec
  plan_buildspec               = var.plan_buildspec
  test_buildspec               = var.test_buildspec
  apply_buildspec              = var.apply_buildspec
  destroy_buildspec            = var.destroy_buildspec
  compute_type_for_building    = var.compute_type_for_building
  os_type                      = var.os_type
  docker_image_used            = var.docker_image_used
  region                       = var.region
  key                          = var.key
}
```

2. **Configuration**: Set the input variables according to your project requirements. Refer to the [Inputs](#inputs) section for details on each variable.

3. **Terraform Apply**: Run `terraform init` and `terraform apply` to provision the resources.

### Inputs

- **tags**: (Map) Tags used in this module.
- **namespace_name**: (String) Namespace used in the project.
- **account_id**: (String) AWS account ID used in the module.
- **domain_name**: (String) Domain name used in the module.
- **s3_bucket_name**: (String) S3 bucket name variable.
- ... (continue for all input variables)

### Outputs

- Outputs, if any, can be documented here.

## Example

```hcl
# Example usage of the codepipeline module
module "codepipeline" {
  source = "git::https://github.com/your-repo/path-to-module"

  # Input variables...
}
```

## License

This module is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
