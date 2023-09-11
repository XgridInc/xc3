# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}

output "security_group_ids" {
  description = "Map of security group IDs"
  value = {
    aws_lb_security_group_id     = aws_security_group.lb_sg.id
    serverless_security_group_id = aws_security_group.serverless_sg.id
    private_security_group_id    = aws_security_group.private_sg.id
    public_security_group_id     = aws_security_group.public_sg.id
  }
}

output "public_subnet_ids" {
  description = "List of Public Subnet IDs"
  value       = [for subnet in aws_subnet.public_subnet : subnet.id]
}

output "private_subnet_id" {
  description = "Private Subnet ID"
  value       = [for subnet in aws_subnet.private_subnet : subnet.id]
}
