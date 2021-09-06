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


def delete(event, context):
    # for debug
    print(event)

    data = json.loads(event['body'])
    community_id: str = data.get('communityId')

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

    table = dynamodb.Table(os.environ['COMMUNITY_INFO'])

    try:
        res_delete = table.delete_item(Key={'communityId': community_id})
        print(res_delete)
    except Exception as e:
        print(e.message)
        response_data = {
            'massage': 'Error when item delete'
        }
        response = {
            "statusCode": 500,
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

    response_data = {
        'massage': 'Community-info deleted'
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
