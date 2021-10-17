import datetime
import json
import logging
import os
from decimal import Decimal

import boto3

dynamodb = boto3.resource('dynamodb')

if os.getenv('AWS_LAMBDA_FUNCTION_VERSION') is None:
    dynamodb = boto3.resource('dynamodb',
        region_name="ap-northeast-1",  # localstack用
        endpoint_url="http://localhost:4566",
        aws_access_key_id="DEFAULT_ACCESS_KEY",
        aws_secret_access_key="DEFAULT_SECRET"
    )

def update(event, context):
    data = json.loads(event['body'])
    if 'weight' not in data:
        logging.error("Validation Failed")
        raise Exception("Weight not found")
    if 'sub' not in data:
        logging.error("Validation Failed")
        raise Exception("Sub not found")

    table = dynamodb.Table(os.environ['USER_WEIGHT_TABLE'])

    timestamp = str(datetime.datetime.now())

    res_update = table.update_item(
        Key={
            'cognitoUserSub': data["sub"]
        },
        ReturnValues='UPDATED_NEW',
        UpdateExpression= 'SET #w = :weight, #time = :time',
        ExpressionAttributeNames={
            '#w': 'weight',
            '#time': 'updatedAt'
        },
        ExpressionAttributeValues={
            ':weight': Decimal(data["weight"]),
            ':time': timestamp
        }
    )

    response_data = {
        'massage' : 'Weight updated'
    }

    response = {
        "statusCode": 200,
        'headers': {
            "Content-type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "UPDATE",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(response_data)
    }

    return response
