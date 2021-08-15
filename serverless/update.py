import datetime
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

# 主キーを指定してアップデート
  # 特定の項目(weight,flg)のみアップデート

def update(event, context):
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
        'updatedAt': timestamp,
    }

    res_update = table.update_item(
        Key={
            'cognitoUserSub': data["sub"]
        },
        ReturnValues='UPDATED_NEW',
        UpdateExpression= 'SET #w = :weight, #flg = :flg, #time = :time',
        ExpressionAttributeNames={
            '#w': 'weight',
            '#flg': 'nextTotalingFlg',
            '#time': 'updatedAt'
        },
        ExpressionAttributeValues={
            ':weight': data["weight"],
            ':flg': 'T',
            ':time': timestamp
        }
    )

    response_data = {
        'massage' : 'Weight updated'
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(response_data)
    }

    return response
