# **Tagging Compliance**

This set of Lambda functions is designed to help you manage your AWS resources more efficiently. The functions can be used together to fetch a list of resources in all AWS regions and then create a dictionary of resources on which provided set of tags are missing in all AWS regions.

## **Tagging Compliance Workflow**
![tagging-compliance](https://user-images.githubusercontent.com/114464405/235908131-25905aa5-7ca0-4e76-8fbd-55c052cfa6b7.png)

## **Resource List: Fetch Resources in All AWS Regions**

This Lambda function allows you to fetch a list of resources in all AWS regions. It returns a dictionary containing the list of resources in a specific AWS region.

To use this function, you can simply invoke it with the appropriate input parameters. The function will then make a request to AWS to fetch a list of resources in all regions and return the results in a dictionary.

## **Resource Parsing: Create Dictionary of Resources Missing Provided Tags in All AWS Regions**

This Lambda function creates a dictionary of resources on which provided set of tags are missing in all AWS regions. It takes a list of resources in all AWS regions as input and returns a dictionary containing the list of resources on which provided tags are missing.


## **Conclusion**

These two Lambda functions can be used together to help you manage your AWS resources more efficiently. By fetching a list of resources in all regions and then creating a dictionary of resources on which provided tags are missing, you can quickly identify and manage your resources in a more organized and effective way.

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
