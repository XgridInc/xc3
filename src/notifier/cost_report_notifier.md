# Introduction:

Notifications are an essential feature in modern software development that help keep team members informed about critical updates and events. In XC3, we use Slack as our primary communication platform, and it's essential to have notifications integrated with Slack channels. In this guide, we will explore how to configure notifications in XC3 using the open-source library, Apprise.

# 1. Apprise:

Apprise is a Python library that makes it easy to send notifications to various services, including Slack, email, and SMS. It's a flexible and straightforward library that allows us to integrate XC3 with Slack seamlessly. By automatically fetching and transforming cost reports and sending them to Slack, the Cost Report Notifier application streamlines the monitoring process and helps to proactively identify and address any cost concerns. For more information please visit [apprise-github](https://github.com/caronc/apprise).

# 2. Notification Workflow:

The XC3 backend utilizes an event-driven serverless architecture to generate cost reports, which are stored in an S3 bucket. A Cost Report Notifier application is scheduled to run on a regular basis using AWS EventBridge. When the application runs, it retrieves the reports from the S3 bucket and transforms them into markdown tables for easier readability.

Once the reports have been transformed, the Cost Report Notifier uses the apprise library to send the reports to a designated Slack channel. This ensures that the relevant team members are alerted to any potential cost issues and can take appropriate action as needed.

<img src="https://user-images.githubusercontent.com/95742163/235850803-6c6f12cc-008a-4ce8-878b-34ffedf3efd0.png" width="600">

# 3. Configuration Steps:

## Prerequisites:

Before we begin configuring notifications, we need to make sure that we have the following:

- A Slack workspace with administrative privileges to create and manage applications and webhooks.
- An S3 bucket containing data related to Account, Project, and Cost of expensive services that will be sent to slack channels.

## Configuration

1.  Create a Slack Bot App:
    To create and install a new Slack app for your workspace and obtain a Bot User OAuth Access Token, follow these steps:

    - Go to the Slack API website and create a new Slack app by providing a name and selecting the workspace where you want to install it.
    - Once created, navigate to the "OAuth & Permissions" section and add the following scopes: "chat:write" and "incoming-webhook."
    - Install the app to your workspace by clicking the "Install App" button.
    - Make a note of the "Bot User OAuth Access Token" provided by Slack, as you will need it later to authenticate your bot and allow it to access the necessary APIs.
    - Configure any additional settings for your app as needed, such as customizing the display name or icon.

2.  Configure the Slack Webhook:
    To set up incoming webhooks in your Slack app and configure notifications to be sent to a specific channel, follow these steps:

    - Navigate to the "Incoming Webhooks" section of your Slack app and enable it.
    - Create a new webhook by selecting the channel where you want to receive the notifications.
    - Make a note of the "Webhook URL" provided by Slack, as you will need it later to configure your notification system.

3.  Fetch data from S3 Bucket:
    To fetch and convert data related to Account, Project, and Cost of expensive services from an S3 bucket, follow these steps:

    - Write a script that retrieves the data from the S3 bucket using appropriate AWS SDKs or APIs.
    - Extract the data related to Account, Project, and Cost of expensive services from the retrieved data.
    - Convert the extracted data into tables that are easy to read and understand. You can use a library such as pandas to create tables in a variety of formats, such as CSV or HTML.
    - Ensure that the tables contain relevant information and are properly formatted for readability.
    - Save the tables to a variable, file or upload them to another S3 bucket for further processing or analysis.

4.  Integrate Apprise with XC3:
    To send notifications containing converted tables from an S3 bucket to a Slack channel using AWS Lambda, follow these steps:

    - Install the Apprise library using pip: pip install apprise.
    - In your script, import the Apprise library and set up a notification object using the Slack webhook URL that you obtained earlier.
    - Load the converted tables from the S3 bucket into the script.
    - Use the notification object to send the tables as a notification message to the Slack channel.
    - Test the notifications by running the script.
    - To make the Apprise library available to the Lambda function, wrap it in an AWS Lambda layer.
    - Create a Lambda function and include the script in the function.
    - Attach the Apprise Lambda layer to the function and configure the function to trigger on a schedule or event.
    - To automate the process of sending reports to a Slack channel, create an EventBridge rule that triggers the Lambda function at a specific schedule.

       <img src="https://user-images.githubusercontent.com/95742163/235852650-9eb90936-4fcb-4695-a822-faa2a13a4cea.png" width="600">

# Conclusion:

In conclusion, setting up notifications with Slack using Apprise is a straightforward process that can greatly improve your experience with XC3. By creating a Slack bot app and integrating its webhook with external services, you can receive notifications about your cost-sensitive metrics like account, project, and expensive services from the S3 bucket directly in Slack. With the added benefit of converting the data into tables and sending them to Apprise, you can easily keep track of important information and stay on top of any potential issues. Overall, notifications are a key feature of XC3 that can help you streamline your workflow and make the most of your time.

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
