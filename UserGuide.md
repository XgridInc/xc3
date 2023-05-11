Welcome to the User Guide for XC3 Project. This guide provides introduction, instructions and information on how to use the XC3 grafana dashboards effectively.

## What is XC3?

Xgrid Cloud Cost Control is a cloud agnostic and risk-free package offering powered by Cloud Custodian that provides security enforcement, tagging, unused or invalid resources cleanup, account maintenance, cost control, and backups. It supports managing AWS public cloud environments and provides a visualization of the usage of resources in account with the support of managing resource utilization on a click.

## How to Use XC3

Once XC3 infrastructure deployed in your AWS Account, Users needs to be added in Cognito pool with requested role (admin/editor/viewer) in respective cognito group. User get random username/password from cognito then he/she can set password on domain by sign in using random credentials.

### User Role Guidelines

Admin Role:

Admins have full access to all features and settings in Grafana. They can create, edit, and delete users, dashboards, data sources, and alerts. They also have the ability to manage permissions and set up LDAP authentication.

Editor Role:

Editors can create and edit dashboards, but they cannot manage users or change system settings. They can also create and manage data sources and alerts that they have access to. However, they do not have access to system-level data sources or alerts.

Viewer Role:

Viewers have read-only access to Grafana. They can view dashboards and panels, but they cannot make any changes. They also do not have access to any administrative or editing functions.

## Getting Started with XC3

Once you've logged in on XC3, you can start using dashboards.

### Home

On Home Page, you can get high-level detail of your AWS Account

- To determine the AWS Account Cost, select the account id and get total spend of AWS Account from last three months
  ![image](https://github.com/TeamXgrid/xc3/assets/122358742/671a7dcc-596c-4f26-b409-00b290137d7b)

- To determine the total spend on AWS for a particular project select the AWS account and project to get the cost of that specific project from the last 14 days.
  ![image](https://github.com/TeamXgrid/xc3/assets/122358742/32560b60-6a43-41a3-ae81-94112596ba65)

- To get the top 5 most expensive services in a specific AWS Region, select an AWS account and AWS region to get the top 5 most expensive services in that region from the last 14 days.
  ![image](https://github.com/TeamXgrid/xc3/assets/122358742/4634ade9-b457-4482-b5b0-9b17c805767e)

### IAM Roles Dashboard
- By selecting IAM Role Dashboard you can view a list of IAM Roles by selecting AWS Account.
  ![image](https://github.com/TeamXgrid/xc3/assets/122358742/fb6d20b8-77a3-4415-a0f7-4998bde32303)
- By selecting a specific IAM Role in a specific AWS Region you can view the resources, state of resources, and the cumulative cost of resources from the last 14 days associated with a specific IAM Role in the selected AWS Region.
  ![image](https://github.com/TeamXgrid/xc3/assets/122358742/fa1eb7c7-e745-4926-b762-bb6d6051a3c9)
- By selecting a specific resource, you can view the detailed billing of that resource from the last 14 days.
  ![image](https://github.com/TeamXgrid/xc3/assets/122358742/31247b0f-b844-456e-bb8f-cf646f30928f)

### IAM Users Dashboard
- By selecting IAM User Dashboard you can view a list of IAM Users by selecting AWS Account.
- By selecting a specific IAM User in a specific AWS Region you can view the resources, state of resources, and the cumulative cost of resources from the last 14 days spin up by a specific IAM User in the selected AWS Region.
- By selecting a specific resource, you can view the detailed billing of that resource from the last 14 days.
- By selecting the specific IAM User in a specific AWS Region you can get the total spend in that AWS Region by specific IAM User.

### Tagging Compliance Dashboard
- By selecting Tagging Compliance Dashboard you can view the resource inventory that is non-conformant to tagging policies setup using following tags:
    - Creator
    - Owner
    - Project

- By selecting Tagging Compliance Dashboard you can view the resource inventory that is non-conformant to tagging policies setup using following tags: - Creator - Owner - Project

      in a specific AWS Region by selecting AWS Account and AWS Region.

  ![image](https://github.com/TeamXgrid/xc3/assets/122358742/28835c64-cf01-4d96-9b04-01d4bcc75bb1)

## Community Support

If you have any questions or run into issues while using XC3, you can ask for help by reaching out on Slack <a href="https://app.slack.com/client/T051FMAMBPU/C051CPC6DHT?cdn_fallback=1">XC3</a>

We hope this guide helps you get started with XC3. If you have any feedback or suggestions for the project, please let us know!

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
