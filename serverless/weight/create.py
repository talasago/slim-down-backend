import json
import logging
import os
import datetime
import jwt
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

def create(event, context):
    print(event)
    data = json.loads(event['body'])

    token = event['headers']['Authorization']
    decoded_token = jwt.decode(token, algorithms=["RS256"], options={"verify_signature": False})
    sub = decoded_token['sub']

    if 'weight' not in data:
        logging.error("Validation Failed")
        raise Exception("Weight not found")
    if sub == "" or sub is None:
        logging.error("Validation Failed")
        raise Exception("Sub not found")

    table = dynamodb.Table(os.environ['USER_WEIGHT_TABLE'])

    timestamp = str(datetime.datetime.now())

    item = {
        'cognitoUserSub': sub,
        'weight': Decimal(data["weight"]),
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    # デバッグ用
    print(item)

    # TODO:subと同じものが存在したらエラーにしたい
    table.put_item(Item=item)

    response_data = {
        'massage' : 'Weight created'
    }

    response = {
        "statusCode": 200,
        'headers': {
            "Content-type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(response_data)
    }

    return response
