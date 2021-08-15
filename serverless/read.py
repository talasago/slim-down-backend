import json
import logging
import os

import boto3

dynamodb = boto3.resource('dynamodb')

if os.environ['IS_OFFLINE']:
    dynamodb = boto3.resource('dynamodb',
        region_name="localhost",
        endpoint_url="http://localhost:8000",
        aws_access_key_id="DEFAULT_ACCESS_KEY",
        aws_secret_access_key="DEFAULT_SECRET"
    )

def get(event, context):
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

    response = {
        "statusCode": 200,
        "body": json.dumps(item['Item'])
    }

    return response
