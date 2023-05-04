## Policy README: SQS Notification Configuration

This configuration file defines the SQS notification configuration for Cloud Custodian in the AWS account. It specifies the following parameters:

- `queue_url`: The URL of the Amazon SQS queue to which Cloud Custodian will send notifications.
- `role`: The Amazon Resource Name (ARN) of the IAM role that Cloud Custodian will use to send notifications to the SQS queue.
- `from_address`: The email address from which notifications will be sent.

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
