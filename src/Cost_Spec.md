# XC3 Specification

The XC3 Spec is a standardized, vendor-agnostic framework that enables accurate measurement and allocation of infrastructure, aimed at facilitating cloud cost control initiatives.

## Introduction

Managing billing details within an AWS environment can be a challenging task, especially when it comes to accurately tracking and allocating costs across various resources and services. With a wide range of services available and varying usage patterns, it can be difficult to determine where costs are being incurred and who is responsible for them.

As an organization's AWS usage increases, cost control becomes a crucial aspect of operations. Accurately measuring and allocating costs to specific teams or projects is essential for effective budgeting and resource allocation. To address this challenge, we offer a methodology for vendor-agnostic and precise measurement and allocation of costs within an AWS environment.

## Foundational definitions

**Total Account Cost** represent total cost of AWS Account. AWS Account Total Costs can be further segmented into **Resource Allocation Costs** and **Resource Usage Costs**. Resource Allocation Costs are expenses that accumulate based on the amount of time provisioned irrespective of usage (e.g. CPU hourly rate) whereas Resource Usage Costs refer to the costs associated with the usage of resources (e.g. compute instances, storage, networking, and data transfer). These costs are incurred based on the amount of resources used, and are typically charged on a pay-per-use basis. Costs for an individual Asset are the summation of it’s Resource Allocation and Usage Costs, e.g. a lambda's cost is equal to Invocation count + Duration of execution + Memory allocation + Request and response sizes. **Pricing model** The pricing model for the service, which can vary depending on factors such as the instance type, region, or usage volume. **Discounts and savings plans** Any discounts or savings plans that you have in place, such as Reserved Instances or Savings Plans. **Taxes** Any applicable taxes, which can vary by region.

<table>
  <tr>
   <td><strong>Total Account Cost</strong>
   </td>
   <td><strong>=</strong>
   </td>
   <td><strong>Resource Allocation Costs</strong>
   </td>
   <td><strong>+</strong>
   </td>
   <td><strong>Resource Usage Costs</strong>
   </td>
   <td><strong>+</strong>
   </td>
   <td><strong>Discount and Savings Plan</strong>
   </td>
   <td><strong>+</strong>
   </td>
   <td><strong>Taxes</strong>
   </td>
  </tr>
</table>

The following chart shows these relationships:
<img src="https://user-images.githubusercontent.com/114464405/235584557-ae662f25-c7d6-4e75-a63d-6472843be259.png">

## Account Total Cost

Account Total Costs consist of Resource Allocation Costs and Resource Usage Costs. Every resource conforming to this specification MUST include at least one cost component with Amount, Unit and Rate attributes as well as a TotalCost value.

Attributes that can impact resource allocation costs include:

* Resource type: The type of AWS resource being reserved or provisioned can impact the cost. Different resource types have different pricing structures, and some resources may be more expensive than others.

* Reservation type: AWS offers different types of reservations, such as Standard or Convertible Reserved Instances, which can impact the cost.

* Term length: AWS offers different term lengths for reservations, ranging from 1 year to 3 years, which can impact the cost.

* Upfront payment: AWS offers the option to pay upfront for reservations, which can result in a discount.

* Payment option: AWS offers different payment options for reservations, including all upfront, partial upfront, or no upfront payments.
So For Resource Allocation Costs:

Total Cost = Upfront Payment + Hourly Rate x Usage Hours

Where:
* [float] Upfront Payment-  The one-time upfront payment made when reserving the resource.
* [float] Hourly Rate -  The rate charged per hour for the reserved resource.
* [float] Usage Hours -  The number of hours the resource is used over the term of the reservation.

Attributes that can impact resource usage costs include:

* Resource type: The type of AWS resource being used can impact the cost. Different resource types have different pricing structures, and some resources may be more expensive than others.

* Usage duration: The amount of time a resource is used can impact the cost. AWS typically charges by the hour or by the second, depending on the resource type.

* Instance size: For compute resources such as EC2 instances, the instance size can impact the cost. Larger instances with more CPU, memory, and storage typically cost more than smaller instances.

* Usage frequency: The frequency with which resources are used can impact the cost. AWS charges based on the actual usage of resources, so frequent usage may result in higher costs.

* Data transfer: The amount of data transferred into and out of AWS resources can impact the cost. AWS charges for data transfer based on the amount of data transferred and the distance it travels.

* Application load: The amount of load generated by applications running on AWS resources can impact the cost. Higher application load may require more resources, which can increase costs.
So For Resource Usage Costs:

Total Cost = Usage (hours or seconds) x Rate + Additional Costs

Where:
* [float] Usage-  The amount of time a resource is used, measured in hours or seconds, depending on the resource type.
* [float] Rate -  The cost per unit of usage, which varies based on the resource type, instance type, region, and other factors.
* [float] Additional Costs -  Other costs associated with using AWS resources, such as data transfer fees, storage costs, and fees for using other AWS services.

Below is an example input when measuring resource total costs over a designated time window (e.g. 24 hours) with AWS billing models:

An organization that needs to run a web application on Amazon EC2 instances. They have determined that they need to use four instances to handle the expected traffic to their application.

To calculate the resource allocation cost of an EC2 instance using unblended metrics, you can use the following API call:

```
aws ce get-cost-and-usage \
--time-period Start=2022-01-01,End=2022-01-31 \
--granularity DAILY \
--metrics "UnblendedCost" \
--filter '{
    "Dimensions": {
        "Key": "USAGE_TYPE_GROUP",
        "Values": ["EC2: Upfront Fee"]
    },
    "Tags": {
        "Key": "Name",
        "Values": ["My EC2 Instance"]
    }
}' \
--group-by Type=DIMENSION,Key=REGION \
--output json
```

This API call retrieves the resource allocation cost for the EC2 instance for the specified time period, broken down by region. The filter is used to specify that we want to retrieve the cost data for the upfront fee usage of the EC2 instance, and that we want to filter the data by the instance name tag with a value of "My EC2 Instance". The response will include the unblended cost, which represents the total cost of resource allocation.

To calculate the resource usage cost of an EC2 instance using unblended metrics, you can use the following API call:

```
aws ce get-cost-and-usage \
--time-period Start=2022-01-01,End=2022-01-31 \
--granularity DAILY \
--metrics "UnblendedCost" \
--filter '{
    "Dimensions": {
        "Key": "USAGE_TYPE_GROUP",
        "Values": ["EC2: Running Hours"]
    },
    "Tags": {
        "Key": "Name",
        "Values": ["My EC2 Instance"]
    }
}' \
--group-by Type=DIMENSION,Key=REGION \
--output json
```

This API call retrieves the resource usage cost for the EC2 instance for the specified time period, broken down by region. The filter is used to specify that we want to retrieve the cost data for the running hours usage of the EC2 instance, and that we want to filter the data by the instance name tag with a value of "My EC2 Instance". The response will include the unblended cost, which represents the total cost of resource usage.

By summing up the resource allocation and usage costs and any additional costs, you can calculate the total cost of running the EC2 instance for a month

## Notes

- Resource **usage** costs cannot be part of idle cost because they are always used, the corresponding resource never "sits idle."
- You can view your costs and usage using the Cost Explorer user interface free of charge. You can also access your data programmatically using the Cost Explorer API. Each paginated API request incurs a charge of `$0.01`. You can't disable Cost Explorer after you enable it.
