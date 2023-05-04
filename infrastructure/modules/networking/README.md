# Terraform Networking Module
The Terraform Networking Module is used to create a Virtual Private Cloud (VPC) in AWS with public and private subnets. It includes the creation of an internet Gateway, NAT Gateway, and Route Tables to enable communication between resources within the VPC and the internet. The module also allows the user to define custom tags and namespace for the resources created.

### Usage
The Networking Module can be used by calling the module block and passing the required input variables in `main.tf`, as shown below:
```
module "networking" {
  source = "./modules/networking"
  vpc_cidr_block            = "10.0.0.0/16"
  public_subnet_cidr_block  = {
    "us-west-2a" = "10.0.1.0/24"
    "us-west-2b" = "10.0.2.0/24"
    "us-west-2c" = "10.0.3.0/24"
  }

  private_subnet_cidr_block = "10.0.4.0/24"
  namespace                 = "myproject"
  tags = {
    "Project" = "example"
    "Owner"       = "JohnDoe@example.co"
  }

}

```

### Input Variables

## Terraform Input Variables

| Variable name             | Description                                                  | Type      | Default | Required |
| -------------------------| --------------------------------------------------------------| ---------| ------- | ---------|
| vpc_cidr_block            | The IP range of the VPC.                                      | `string`  | `null`  | Yes      |
| public_subnet_cidr_block  | A map of public subnet CIDR blocks, keyed by availability zone.| `map(string)`    | `null`  | Yes      |
| private_subnet_cidr_block | The CIDR block of the private subnet.                          | `string`  | `null`  | Yes      |
| namespace                 | The namespace to use for the resources created.               | `string`  | `null`  | Yes      |
| tags                      | A map of custom tags to apply to the resources created.        | `map(string)`    | `null`  | Yes      |


### Output Variables

| Variable name        | Description                                                   |
| ---------------------|--------------------------------------------------------------|
| vpc_id                |  The ID of the VPC.                                            |
| public_subnet_ids     |  A list of the IDs of the public subnets.                      |
| private_subnet_id     |  The ID of the private subnet.                                  |
| security_group_ids    |  The map of the security group IDs.                             |


### Resources Created

- aws_vpc: The VPC resource.

- aws_subnet: The public and private subnet resources.

- aws_internet_gateway: The internet Gateway resource.

- aws_route_table: The public and private Route Table resources.

- aws_nat_gateway: The NAT Gateway resource.

- aws_security_groups: The security group resource.

### Dependencies

This module depends on the following provider:

- aws: The official AWS provider for Terraform.

### Limitations

The module currently only supports creating a single private subnet.
The module does not include any network ACLs.

### License

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
