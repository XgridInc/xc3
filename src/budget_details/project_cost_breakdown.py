import json
import logging
import os
import time
from datetime import date, timedelta

import boto3
import botocore
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

def lambda_handler(event, context):
    print(event)
    return "Hello from project breakdown"