##################################################
# tfvars
##################################################


namespace_name = "example"
account_id     = "your-account-id"
domain_name    = "your-domain"

s3_bucket_name = "terraform-state-xc3-example-pipeline"


xc3_codepipeline_role  = "arn:aws:iam::201635854701:role/xccc-pipeline-role"
codebuild_service_role = "arn:aws:iam::201635854701:role/service-role/codebuild-test-service-role"
codestar_connections   = "arn:aws:codestar-connections:eu-west-1:201635854701:connection/68b68fa1-9687-405a-b75c-cbf1f5ca6de5"

approve_comment_for_apply   = "This approval needs to create XC3 infrastructure."
approve_comment_for_destroy = "This approval needs to destroy XC3 infrastructure."

full_repository_id = "your full repo id"
full_branch_name   = "feature/pipeline-testing-example"

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
