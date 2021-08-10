import json
import logging
import os
import datetime

import boto3

dynamodb = boto3.resource('dynamodb')

if os.environ['IS_OFFLINE']:
    dynamodb = boto3.resource('dynamodb',
        region_name="localhost",
        endpoint_url="http://localhost:8000",
        aws_access_key_id="DEFAULT_ACCESS_KEY",
        aws_secret_access_key="DEFAULT_SECRET"
    )

def create(event, context):
    data = json.loads(event['body'])
    if 'weight' not in data:
        logging.error("Validation Failed")
        raise Exception("Weight not found")
    if 'sub' not in data:
        logging.error("Validation Failed")
        raise Exception("Sub not found")

    table = dynamodb.Table(os.environ['DynamodbTableWeight'])

    timestamp = str(datetime.datetime.now())

    item = {
        'cognitoUserSub': data["sub"],
        'nextTotalingFlg': "T",
        'weight': data["weight"],
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    table.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }

    return response
