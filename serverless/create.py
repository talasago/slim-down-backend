import json
import logging
import os
import time
import uuid

import boto3

dynamodb = boto3.resource('dynamodb')

def create(event, context):
    data = json.loads(event['body'])
    if 'text' not in data:
        logging.error("Validation Failed")
        raise Exception("Text not found")

    timestamp = str(time.time())

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    item = {
        'id': str(uuid.uuid1()),
        'text': data['text'],
        'checked': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    table.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }

    return response
