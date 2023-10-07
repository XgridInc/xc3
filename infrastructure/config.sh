#!/usr/bin/env bash

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

# Variables values that will be used in init script to create resources for XC3 infrastructure
export aws_region="eu-west-1"
export dynamo_table_name="terraform-lock"
export bucket_name="terraform-state-xc3"
export project="example"
export domain="example.test.co"
export owner_email="admin@test.co"
export creator_email="admin@test.co"
export namespace="example"
export env="prod"
