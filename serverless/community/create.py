import json
import os
import datetime
import boto3

dynamodb = boto3.resource('dynamodb')
if os.getenv('IS_OFFLINE') is not None or \
   os.getenv('AWS_LAMBDA_FUNCTION_VERSION') is None:
    dynamodb = boto3.resource('dynamodb',
                              region_name="ap-northeast-1",  # localstack用
                              endpoint_url="http://localhost:4566",
                              aws_access_key_id="DEFAULT_ACCESS_KEY",
                              aws_secret_access_key="DEFAULT_SECRET"
                              )


def create(event, context):
    # for debug
    print(event)

    data = json.loads(event['body'])
    community_id: str        = data.get('communityId')    # noqa: E221
    community_name: str      = data.get('communityName')  # noqa: E221
    # TOOD:subはjwtのトークンのsubをもとにすべき
    community_owner_sub: str = data.get('communityOwnerSub')
    content: str             = data.get('content')         # noqa: E221

    if community_id == "":
        response_data = {
            'massage': 'Community-id is required'
        }

        response = {
            "statusCode": 400,
            'headers': {
                "Content-type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date, \
                Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Credentials": "true"
            },
            "body": json.dumps(response_data)
        }
        return response

    if community_name == "":
        response_data = {
            'massage': 'Community-name is required'
        }

        response = {
            "statusCode": 400,
            'headers': {
                "Content-type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date, \
                Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Credentials": "true"
            },
            "body": json.dumps(response_data)
        }
        return response

    timestamp = str(datetime.datetime.now())

    item = {
        'communityId': community_id,
        'communityName': community_name,
        'communityOwner': community_owner_sub,
        'content': content,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    # デバッグ用
    print(item)

    table = dynamodb.Table(os.environ['COMMUNITY_INFO'])
    # TODO:subと同じものが存在したらエラーにしないといけない
    table.put_item(Item=item)

    response_data = {
        'massage': 'Community-info created'
    }

    response = {
        "statusCode": 200,
        'headers': {
            "Content-type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date, \
                Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(response_data)
    }

    return response
