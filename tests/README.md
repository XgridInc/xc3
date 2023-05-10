## Introduction

For XC3 we are using pytest for testing, and we have provisioned our infrastructure using Terraform. Additionally, we are using the Boto3 client library to interact with AWS services programmatically.

In the following sections, we will explore how to use these tools to test our application effectively and efficiently. We will cover topics such as defining test cases, running tests, and analyzing test results. We will also discuss leveraging Terraform to create and manage the test environment and how Boto3 can help us interact with AWS services during testing.

By the end of this guide, you should understand how to use pytest, Terraform, Boto3 and mock to test your application, and how these tools can help you achieve better software quality and reliability.

## How will the tests be run?

Tests will be run frequently throughout the development cycle, including during the build and deployment stages. It's a good practice to run tests after each code change and before each deployment to ensure that the changes don't introduce any new bugs or regressions. We have automated this process using GitHub Actions, which allows us to set up a workflow that automatically tests our code whenever changes are pushed to the repository. With GitHub Actions, you can define custom workflows in YAML files that specify the steps to run and the conditions under which they should be run. In our case, we have defined a workflow that runs the pytest command to execute the test suite whenever changes are pushed to the repository. The results of the test run are available in the GitHub Actions console, where developers can view logs and other diagnostic information.

## Where will the tests be run?


Running tests on a stable branch such as `main` is crucial to ensure that only tested and working code is released. The tests can be configured to run automatically on every push request made to the main branch. This can be achieved by adding the following section to the GitHub Actions workflow YAML file:

```
  on:
    push:
        branches: [ main ]

```
However, running tests on unstable feature branches is equally important to catch any potential bugs early in the development process. To run tests on a feature branch, you can modify the YAML file to include the feature branch name in the branches section:

```
  on:
    push:
        branches: [ feature/unit-test-infra ]

```

Regardless of the branch where the tests are run, they will be executed on a remote server or a containerized environment, which is provisioned and managed by the GitHub Actions Runner. The runner provides a scalable and flexible environment for running tests, and it can be configured to run tests in parallel to reduce testing time. The results of the test run are available in the GitHub Actions console, where developers can view logs and other diagnostic information.

## Contributing to the test suite

Anyone can contribute to the test suite by adding new test cases or improving existing ones. To contribute, you can fork the project repository on GitHub and create a new branch for your changes. Then, you can make your changes to the test files and commit them to your branch. Once you're ready to submit your changes, you can create a pull request from your branch to the main branch of the project repository. The pull request will be reviewed by the project maintainers, who will provide feedback and suggestions for improvement. Once the changes are approved, they will be merged into the main branch and become part of the project's test suite. It's important to follow the project's standards and guidelines for writing test cases, as well as any specific conventions or patterns used in the project.

## Work Flow

1. Code changes are pushed to the repository.
2. GitHub Actions detects the changes and triggers the workflow.
3. The workflow checks out the latest version of the code from the repository.
4. GitHub Actions provisions a runner and installs the necessary dependencies for the project.
5. The runner runs the pytest command to execute the test suite.
6. If any tests fail, the workflow is halted, and a notification is sent to the developers.
7. If all tests pass, the workflow moves on to the next stage, such as deploying the code to the production environment.
8. The results of the test run are available in the GitHub Actions console, where developers can view logs and other diagnostic information.

## Testing Work Flow


![image](https://user-images.githubusercontent.com/105271892/234582908-831eb98c-8257-4bc7-8b51-a8a1b040b4b3.png)

## Github Actions Workflow Overview

![image](https://github.com/X-CBG/X-CCC/assets/122358742/ff37c233-7961-40ef-9759-bc642651ae22)

Here is a possible flow for the case where the tests fail and the changes need to be fixed before the PR can be approved and merged:

1. Create PR: The developer creates a new pull request in GitHub with their changes.
2. GitHub Action runs: When the PR is created, the GitHub Action is triggered automatically.
3. Run unit tests: The GitHub Action runs the unit tests defined in the project to verify the changes made in the PR.
4. Test failure: If the tests fail, the GitHub Action reports the failure and the PR is marked as failing the tests.
5. Fix the code: The developer needs to fix the code to make the tests pass.
6. Commit changes: Once the code is fixed, the developer commits the changes to the same branch used for the original PR.
7. GitHub Action runs again: As soon as the changes are committed, the GitHub Action is triggered again automatically.
8. Rerun unit tests: The GitHub Action runs the unit tests again to verify the changes made in the commit.
9. Test success: If the tests pass, the PR is marked as passing the tests and can be reviewed again.
10. Review: The code changes are reviewed by the team, and if approved, the PR is merged into the main branch.
