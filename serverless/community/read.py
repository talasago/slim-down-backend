import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
if os.getenv('IS_OFFLINE') is not None or \
   os.getenv('AWS_LAMBDA_FUNCTION_VERSION') is None:
    dynamodb = boto3.resource('dynamodb',
                              region_name="localhost",
                              endpoint_url="http://localhost:8000",
                              aws_access_key_id="DEFAULT_ACCESS_KEY",
                              aws_secret_access_key="DEFAULT_SECRET"
                              )


def get_list(event, context):
    table = dynamodb.Table(os.environ['COMMUNITY_INFO'])

    scaned_res: dict = table.scan(
        ProjectionExpression="communityId,   \
                              communityName, \
                              communityOwner, \
                              content"
    )
    # ホントはページネーション対応が必要。LastEvaluated

    items = scaned_res.get('Items')
    print(scaned_res)

    response_data = {
        'items': items
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
