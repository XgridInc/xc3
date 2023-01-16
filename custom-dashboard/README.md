# Resource Inventory
This code is a AWS Lambda function written in Python that takes in an event and context as input. 
The function retrieves the tags of EC2 instances in a specified region and sends
a list of the instances to another Lambda function for cost analysis. It uses the boto3 library to 
interact with the AWS services. The function first retrieves the region name from the input event body,
which is in JSON format. It then uses the resource group tagging API and the boto3 library to get the resources 
in the specified region, and filters the resources to only show EC2 instances. It then parses the response and 
creates a list of the instances' ARNs.It then invokes another Lambda function passing the region and the list 
of instances as the payload and waits for the response. It returns the response from the second Lambda function as a
JSON object, including the headers for CORS.

# Resource Cost and Status
This code is a AWS Lambda function written in Python that takes in an event and context as input.
The function retrieves the cost and usage of resources in the AWS region specified in the event.
The function first checks if the input data is empty and assigns an empty dictionary in that case.
If the input data is not empty, it then connects to the AWS EC2 service using the boto3 library and retrieves
the state of the resources specified in the input data. It also splits the resource IDs and retrieves the cost
and usage data of these resources from the Cost Explorer service using the boto3 library.
Finally, the function returns a JSON object containing the resource ID, cost, and status of the resources.

# Resource State Change
This code is a AWS Lambda function written in Python that takes in an event and context as input. 
The function starts or stops an EC2 instance based on the request sent in the event. It uses the boto3
library to interact with the AWS EC2 service. The function first retrieves the instance ID and status of 
the instance from the input event body, which is in JSON format. It then parses the instance ID to extract 
the actual instance ID and uses that to start or stop the instance by calling the appropriate method on the EC2 client. 
Finally, it returns the response from the EC2 service in the form of a JSON object, including the headers for CORS.