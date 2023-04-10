# Pre-Commit Hooks

This repository includes several pre-commit hooks to help enforce code quality and best practices. These hooks will be run automatically when you run git commit.

## Install the following in your system

- pre-commit>=2.0.0

```sh
cd <repo_directory>
pip install pre-commit
```

- shellcheck:
  Visit this [link](https://github.com/koalaman/shellcheck#installing) for detailed installation instructions.
- Terraform-docs:
  Visit this [link](https://terraform-docs.io/user-guide/installation/) for detailed installation instructions.
- Terraform-lint: Visit this [link](https://github.com/terraform-linters/tflint) for detailed installation instructions.

## Usage Instructions

Install the pre-commit hooks in your repository home directory:

```sh
pre-commit install -f --config pre-commit-config/.pre-commit-config.yaml
```

## Hooks

---

- **Trailing Whitespace**
  This hook removes any trailing whitespace at the end of lines in your files. This helps keep your code clean and avoids issues with some editors that might add unwanted whitespace.

- **End-of-file Fixer**
  This hook ensures that your files end with a newline character. This is important because some programs might behave unexpectedly if the last line of a file does not end with a newline character.

- **Check YAML**
  This hook checks that your YAML files are valid and conform to a specific structure. This helps ensure consistency across your codebase and avoids issues with parsing invalid YAML.

- **Detect AWS Credentials**
  This hook scans your code for any AWS credentials and alerts you if it finds any. This is important because AWS credentials should not be checked into your code repository for security reasons.

- **Shellcheck**
  This hook checks your shell scripts for common issues and syntax errors. This helps ensure that your scripts will work correctly on different platforms and avoids issues with shell commands that might behave differently depending on the environment.

- **Flake8**
  This hook checks your Python code for syntax errors and style issues. This helps ensure that your code is consistent and adheres to best practices for Python development.

- **Black**
  This hook automatically formats your Python code according to a specific style guide. This helps ensure that your code is consistent and easy to read.

- **Terraform Fmt**
  This hook ensures that your Terraform code is correctly formatted. This helps ensure consistency across your codebase and avoids issues with parsing invalid Terraform.

- **Terraform Validate**
  This hook validates your Terraform code to ensure that it follows best practices and is free from errors. This helps ensure that your Terraform code will work correctly when deployed.

- **Terraform Docs**
  This hook generates documentation for your Terraform code. This helps ensure that your code is well-documented and easy to understand.

- **Terraform Tflint**
  This hook checks your Terraform code for common issues and errors. This helps ensure that your Terraform code is free from errors and follows best practices.

- **Go Fmt**
  This hook ensures that your Go code is correctly formatted. This helps ensure consistency across your codebase and avoids issues with parsing invalid Go.

- **Go Revive**
  This hook checks your Go code for common issues and style violations. This helps ensure that your Go code follows best practices and is free from errors.

- **Go Mod Tidy**
  This hook ensures that your Go module dependencies are correctly managed and up to date. This helps ensure that your code will work correctly when deployed.

- **SQLFluff Lint**
  This hook checks your SQL code for common issues and style violations. This helps ensure that your SQL code follows best practices and is free from errors.

- **Detect Secrets**
  This hook scans your code for any secrets, such as passwords or API keys, and alerts you if it finds any. This is important because secrets should not be checked into your code repository for security reasons.

## Further documentation

### Information/Instructions about pre-commit hooks can be found here

- General: <https://pre-commit.com/> - Provides general information about pre-commit hooks and how to use them.
- Disabling hooks: <https://pre-commit.com/#temporarily-disabling-hooks> - Provides instructions for temporarily disabling pre-commit hooks.

### Information/Instructions about git submodules can be found here

- <https://git-scm.com/book/en/v2/Git-Tools-Submodules>
- <https://devconnected.com/how-to-add-and-update-git-submodules/>
