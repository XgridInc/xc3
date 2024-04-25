import json
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Load the JSON data
with open('dummy_data1.json', 'r') as file:
    data1 = json.load(file)

def push_to_prometheus(data1):
    registry = CollectorRegistry()

    # Create a single gauge with multiple labels
    gauge = Gauge(
        "FED_USER_Resource_Cost_List",
        "FED USER Resource List And Cost",
        labelnames=[
            "resource_id",
            "resource",
            "account_id",
            "region",
            "resource_name",
            "month"
        ],
        registry=registry
    )

    # Iterate through the data and populate the gauge
    for resource in data1['ec2']:
        resource_id = resource['resource_id']
        service = resource['resource']
        cost = resource['cost']
        account_id = resource['account_id']
        region = resource['region']
        month = resource['month']
        resource_name = resource_id.split(':')[-1]

        # Set the gauge value
        gauge.labels(
            resource_id=resource_id,
            resource=service,
            account_id=account_id,
            region=region,
            resource_name=resource_name,
            month=month
        ).set(cost)

    # Push the metrics to Prometheus Pushgateway
    push_to_gateway('localhost:9091', job='pushgateway', registry=registry)

# Call the function to push data to Prometheus
push_to_prometheus(data1)