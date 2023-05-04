# Contributing Guidelines

XC3 welcomes contributions from the community. This document outlines the conventions that should be followed when making a contribution.

## Contact Us

Whether you are a user or contributor, official support channels include the following:

- [Issues](https://github.com/X-CBG/XC3/issues)
- [XC3 Slack](https://app.slack.com/client/T051FMAMBPU/C051CPC6DHT)

Before opening a new issue or submitting a new pull request, it's helpful to search the project -
It's possible that another user has already reported the issue you're facing, or it may be a known issue
that we're already aware of.
It is also worth asking on the Slack channels.

## Where to start?

You can contribute to XC3 in many ways. This includes, but is not limited to:

- Bug and feature reports
- Documentation
- Development of features and bug fixes

## Contribution Process

### Reporting Bugs and Creating Issues

This section outlines how to report bugs and create issues for XC3. To report bugs related to XC3, please file an issue in the `XC3` repository. Please follow the template when filing an issue and provide as much information as possible.

Before reporting a bug, we encourage you to search the existing Github issues to ensure that the bug has not already been filed.

### Code Contributions

This section outlines how to contribute code to XC3. For all changes, regardless of size, please create a Github issue that details the bug or feature being addressed before submitting a pull request. In the GitHub issue, contributors may discuss the viability of the solution, alternatives, and considerations.

#### Contribution Flow

The general steps for making a code contribution to XC3 are as follows:
1. Fork the repository on Github.
2. Create a new branch.
3. Make your changes in organized commits.
4. Integrate pre-commit hooks to sanitize your code.
5. Push your branch to your fork.
6. Submit a pull request to the original repository.
7. Make any changes as requested by the maintainers.
8. Make sure PR is reviewed by OPEN AI PR reviewer.
9. Once accepted by a maintainer, it will be merged into the original repository by a maintainer.

#### Contribution Checklist

When making a contribution to the repository, please ensure that the following is addressed.

1. Code must be sanitized using [pre-commit-hooks](https://github.com/X-CBG/XC3/blob/main/pre-commit-config/.pre-commit-config.yaml)
2. Ensure that all existing GitHub actions pass.
3. Commits are signed (see notes below).
4. Ensure to write tests for any new code addition and to update existing tests when making changes to the codebase.
5. Code must follow the [Open PR AI Reviewer Suggestions](https://github.com/X-CBG/XC3/blob/main/.github/workflows/openai-pr-reviewer.yml).

#### Commit Messages

Commit messages should provide enough information about what has changed and why. Please follow the templates for how this information should be detailed.

#### Sign your commits

The sign-off is a simple line at the end of the explanation for a commit. All commits need to be
signed and verified. Your signature certifies that you wrote the patch or otherwise have the right to contribute
the material. The rules are pretty simple, if you can certify the below (from
[developercertificate.org](https://developercertificate.org/)):

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
1 Letterman Drive
Suite D4700
San Francisco, CA, 94129

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.

Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

Then you just add a line to every git commit message:

    Signed-off-by: Joe Smith <joe.smith@example.com>

Use your real name (sorry, no pseudonyms or anonymous contributions.)

##### Configuring Commit Signing in Git

1. If you set your `user.name` and `user.email` git configs, you can sign your commit with `git commit -s`.

    Note: If your git config information is set properly then viewing the `git log` information for your commit will look something like this:

    ```
    Author: Joe Smith <joe.smith@example.com>
    Date:   Thu Feb 2 11:41:15 2018 -0800

        Update README

        Signed-off-by: Joe Smith <joe.smith@example.com>
    ```

    Notice the `Author` and `Signed-off-by` lines match. If they don't your PR will be rejected by the automated DCO check.

##### Commit Signature Verification

All commit signatures must be verified to ensure that commits are coming from a trusted source. To do so, please follow Github's [Signing commits guide](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits).
