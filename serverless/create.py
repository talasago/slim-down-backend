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

    table = dynamodb.Table(os.environ['WEIGHT_TABLE'])

    timestamp = str(datetime.datetime.now())

    item = {
        'cognitoUserSub': data["sub"],
        'nextTotalingFlg': "T",
        'weight': data["weight"],
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    # TODO:subと同じものが存在したらエラーにしたい
    table.put_item(Item=item)

    response = {
        "statusCode": 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        },
        "body": json.dumps(item)
    }

    return response
