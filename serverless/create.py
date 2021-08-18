import json
import logging
import os
import datetime
import jwt

import boto3

dynamodb = boto3.resource('dynamodb')

if os.getenv('IS_OFFLINE') is not None:
    dynamodb = boto3.resource('dynamodb',
        region_name="localhost",
        endpoint_url="http://localhost:8000",
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

    table = dynamodb.Table(os.environ['WEIGHT_TABLE'])

    timestamp = str(datetime.datetime.now())

    item = {
        'cognitoUserSub': sub,
        'weight': data["weight"],
        'nextTotalingFlg': "T",
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    # TODO:subと同じものが存在したらエラーにしたい
    table.put_item(Item=item)

    response = {
        "statusCode": 200,
        'headers': {
            "Content-type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(item)
    }

    return response
