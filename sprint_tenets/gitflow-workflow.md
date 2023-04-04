# Gitflow Workflow

Gitflow is a legacy Git workflow that was originally a disruptive and novel strategy for managing Git branches. This repository implements Gitflow Workflows for managing code changes in a structured manner.

This workflow doesn’t add any new concepts or commands beyond what’s required for the Feature Branch Workflow. Instead, it assigns very specific roles to different branches and defines how and when they should interact. In addition to feature branches, it uses individual branches for preparing, maintaining, and recording releases. Of course, you also get to leverage all the benefits of the Feature Branch Workflow: pull requests, isolated experiments, and more efficient collaboration.

Below are brief explanations of each workflow, along with additional relevant information and implementation instructions:

## How it Works

---

### **1. Develop and main branches**

This workflow uses two branches to record the history of the project. The `main` branch stores the official release history, and the `develop` branch serves as an integration branch for features. It's also convenient to tag all commits in the `main` branch with a version number.

![Image](https://user-images.githubusercontent.com/95742163/221568481-79588f26-5617-4748-9fcd-ff7225fede94.png)

The first step is to complement the default `main` with a `develop` branch.

```
git branch develop
git push -u origin develop
```

This branch will contain the complete history of the project, whereas the `main` will contain an abridged version. Other developers should now clone the central repository and create a tracking branch for `develop`.

### **2. Feature branches**

Each new feature should reside in its own branch, which can be pushed to the central repository for backup/collaboration. But, instead of branching off of `main`, feature branches use `develop` as their parent branch. When a feature is complete, it gets merged back into `develop`. Features should never interact directly with `main`.

![Image](https://user-images.githubusercontent.com/95742163/221568522-633b63e0-6c0b-4b45-9b20-621ae2bf6baa.png)

**Creating a feature branch:**

```
git checkout develop
git checkout -b feature_branch
```

**Finishing a feature branch:**

When you’re done with the development work on the feature, the next step is to merge the `feature_branch` into `develop`.

```
git checkout develop
git merge feature_branch
```

### **3. Release branches**

Once `develop` has acquired enough features for a release (or a predetermined release date is approaching), you fork a `release` branch off of `develop`. Creating this branch starts the next release cycle, so no new features can be added after this point—only bug fixes, documentation generation, and other release-oriented tasks should go into this branch. Once it's ready to ship, the `release` branch gets merged into `main` and tagged with a version number. In addition, it should be merged back into `develop`, which may have progressed since the release was initiated.
![Image](https://user-images.githubusercontent.com/95742163/221568694-f64f8852-a25d-499a-8c9e-930f5dc21616.png)

Making release branches is another straightforward branching operation. Like feature branches, release branches are based on the `develop` branch. A new release branch can be created using the following methods.

```
git checkout develop
git checkout -b release/0.1.0
```

Once the release is ready to ship, it will get merged into `main` and `develop`, then the `release` branch will be deleted. It’s important to merge back into `develop` because critical updates may have been added to the `release` branch and they need to be accessible to new features.

To finish a `release` branch:

```
git checkout main
git merge --no-ff release/1.0
git tag -a 1.0 -m "Release 1.0"
git push origin main
git push --tags
git branch -D release/1.0
```

### **4. Hotfix branches**

Maintenance or `hotfix` branches are used to quickly patch production releases. Hotfix branches are a similar to `release` branches and feature branches except they're based on `main` instead of develop. This is the only branch that should fork directly off of `main`. As soon as the fix is complete, it should be merged into both `main` and `develop` (or the current `release` branch), and `main` should be tagged with an updated version number.
![Image](https://user-images.githubusercontent.com/95742163/221568745-0cd6a6fd-75df-4f68-9575-377d12b8e3ec.png)

A `hotfix` branch can be created using the following methods:

```
git checkout main
git checkout -b hotfix_branch
```

Similar to finishing a `release` branch, a `hotfix` branch gets merged into both main and develop.

```
git checkout main
git merge hotfix_branch
git tag -a <v1.0.1> -m ""
git push origin main --tags
git checkout develop
git merge hotfix_branch
git branch -D hotfix_branch
```

## Benefits

- Provides a clear separation of concerns and a well-defined process for managing code changes.
- Helps ensure code stability and reliability.
- Facilitates collaboration among developers.
- Encourages testing and integration throughout the development process.
- Allows for quick fixes to critical issues in the `main` branch.

### Summary

---

Some key takeaways to know about Gitflow are:

The workflow is great for a release-based software workflow. Gitflow offers a dedicated channel for hotfixes to production.

The overall flow of Gitflow is:

- A `develop` branch is created from `main`
- A `release` branch is created from `develop`
- Feature branches are created from `develop`
- When a feature is complete it is merged into the `develop` branch
- When the `release` branch is done it is merged into `develop` and `main`
- If an issue in `main` is detected a `hotfix` branch is created from `main`
- Once the `hotfix` is complete it is merged to both `develop` and `main`

## License

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
