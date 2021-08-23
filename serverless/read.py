import json
import logging
import os
from decimal import Decimal

import boto3

dynamodb = boto3.resource('dynamodb')

if os.getenv('IS_OFFLINE') is not None:
    dynamodb = boto3.resource('dynamodb',
        region_name="localhost",
        endpoint_url="http://localhost:8000",
        aws_access_key_id="DEFAULT_ACCESS_KEY",
        aws_secret_access_key="DEFAULT_SECRET"
    )

def get(event, context):
    # デバッグ用
    print(event)

    query_param = event.get('queryStringParameters')  # クエリパラメータ取得

    if query_param == None:
        logging.error("Validation Failed")
        raise Exception("'queryStringParameters' not found")

    sub = query_param.get('sub')
    if sub == None:
        logging.error("Validation Failed")
        raise Exception("Sub not found")

    table = dynamodb.Table(os.environ['WEIGHT_TABLE'])

    item = table.get_item(
        Key={'cognitoUserSub': sub}
    )

    # デバッグ用
    print(item)

    res_body = {
        "weight": item['Item']['weight']
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
        "body": json.dumps(res_body, default=decimal_default_proc)
    }

    return response

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
