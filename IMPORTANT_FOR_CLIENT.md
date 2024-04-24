THIS BRANCH HAS CHANGES MADE TO IT IN:
1. infrastructure / modules / serverless directory, where we have changed the iam-role.tf file for adding three new lambda functions and their role and role policies
  There are also changes made in the variables.tf file for adding the three lambda function file paths. There is also resource definitions for CloudWatch and EventBridge rules as well
2. infrastructure / variables.tf file, where we have added a variable for the lambda function cron job, namely 'roles_lambda_cron'.
3. src / iam-roles directory, where there are three new or extra python files in the directory, for the source code of the threee new Lambda fucntions.

NOTE: THE CODE FOR THE THREE NEW LAMBDA FUNCTIONS HAS ALSO BEEN ZIPPED INTO A FILE NAMED SOURCE_CODE_FOR_IAM_ROLES ALONG WITH THE DASHBOARD FILE IN THE 
ROOT DIRECOTORY WHICH CAN BE PASTED IN THE EXISTING LAMBDA FUNCTIONS IN THE IAM ROLE WORKFLOW TO BE TESTED AND INCORPORATED.
