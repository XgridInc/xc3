# Changelog

All notable changes to the `XgridInc/xc3` repository will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.1.0]  - 2023-07-17


### Changed
- Integrated EIC endpoint and removed bastion host
- Updated the infra-deployment based on environment variable
- Added the automation script to deploy XC3 infrastack
- Updated the Architecture Diagram of XC3 in the Readme file


### Fixed
- Fixed Linked List Lambda to run from a member account as well
- Added checks for the packages installation [AWS CLI, python, terraform] in the init.sh bash script.


## [1.0.1]  - 2023-06-06


### Changed
- Updated the Readme file
- Updated the Architecture Diagram in the Readme file


### Fixed
- SSL Certificate Validation issue
- Fixed the startup script of XC3's EC2 instance




## [1.0.0] - 2023-05-11

### Added
- Initial release of the `XgridInc/xc3` repository.
- `cloud_custodian_policies` folder having cloud custodian policies for tagging compliance, monitoring and alerting
- `Pre-requirements` folder to refer the IAM Permission Set required to setup XC3
- `Infrastructure` folder with the necessary IaC to provision XC3 infrastack
- `src` folder having the XC3 backend
- `tests` folder with unit testing implementation v1.0.0 for terraform infrastructure.
- `workflows` folder which contains the diagram of all the XC3 workflows implemented
- `CODE_OF_CONDUCT.md` file for the Code of Conduct for the community
- `CONTRIBUTING.md` file which contains the detail of how to contribute to the Project
- `ROADMAP.md` file which has information about XC3's existing features and its future plans
- `UserGuide.md` file provides the guide on how to use XC3 Grafana Dashboards effectively

### Changed
- Updated the startup script of XC3's EC2 instance

[1.0.0]: https://github.com/XgridInc/xc3/releases/tag/v1.0.0
[1.0.1]: https://github.com/XgridInc/xc3/releases/tag/v1.0.1
[1.1.0]: https://github.com/XgridInc/xc3/releases/tag/v1.1.0

