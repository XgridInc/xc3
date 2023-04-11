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
  <img width="691" alt="Screenshot 2023-03-29 at 11 53 37 AM" src="https://user-images.githubusercontent.com/114464405/228455340-3611e529-e82f-4b03-9a03-7c1dc1ee6d5f.png">

- To determine the total spend on AWS for a particular project select the AWS account and project to get the cost of that specific project from the last 14 days.
  <img width="695" alt="Screenshot 2023-03-29 at 12 51 19 PM" src="https://user-images.githubusercontent.com/114464405/228464432-bd9a050e-9d9c-464b-818d-cd5d3c31fcff.png">

- To get the top 5 most expensive services in a specific AWS Region, select an AWS account and AWS region to get the top 5 most expensive services in that region from the last 14 days.
  <img width="1364" alt="Screenshot 2023-03-29 at 11 57 55 AM" src="https://user-images.githubusercontent.com/114464405/228455613-ca25079c-b40a-40b7-947b-97ca7e1bee55.png">

### IAM Roles Dashboard
- By selecting IAM Role Dashboard you can view a list of IAM Roles by selecting AWS Account.
  <img width="801" alt="Screenshot 2023-03-29 at 12 01 42 PM" src="https://user-images.githubusercontent.com/114464405/228455871-d9891b72-78fe-4f89-80d2-816471d6a0da.png">
- By selecting a specific IAM Role in a specific AWS Region you can view the resources, state of resources, and the cumulative cost of resources from the last 14 days associated with a specific IAM Role in the selected AWS Region.
  <img width="774" alt="Screenshot 2023-03-29 at 12 05 37 PM" src="https://user-images.githubusercontent.com/114464405/228456236-0e549499-0370-434d-9701-58b0054347ae.png">
- By selecting a specific resource, you can view the detailed billing of that resource from the last 14 days.
  <img width="1157" alt="Screenshot 2023-03-29 at 12 06 31 PM" src="https://user-images.githubusercontent.com/114464405/228456521-6d647805-55a3-4f32-a887-51a4269968ee.png">

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

  <img width="683" alt="Screenshot 2023-03-29 at 12 13 13 PM" src="https://user-images.githubusercontent.com/114464405/228456656-fca6d6cb-2ce4-4dcc-acee-de0c6d3e4458.png">

## Community Support

If you have any questions or run into issues while using XC3, you can ask for help by sending an email to <a href="mailto:xccc@xgrid.co">xccc@xgrid.co</a>

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