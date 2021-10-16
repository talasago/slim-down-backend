import json
import os
import boto3
from datetime import datetime
from decimal import Decimal
import pandas as pd

dynamodb = boto3.resource('dynamodb')
if os.getenv('IS_OFFLINE') is not None or \
   os.getenv('AWS_LAMBDA_FUNCTION_VERSION') is None:
    dynamodb = boto3.resource('dynamodb',
                              region_name="ap-northeast-1",  # localstack用
                              endpoint_url="http://localhost:4566",
                              aws_access_key_id="DEFAULT_ACCESS_KEY",
                              aws_secret_access_key="DEFAULT_SECRET"
                              )
tbl_commu_info = dynamodb.Table(os.environ['COMMUNITY_INFO'])
tbl_commu_weight = dynamodb.Table(os.environ['COMMUNITY_WEIGHT'])


def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def get_list(event, context):
    today = datetime.now().strftime('%Y%m%d')

    scaned_res: dict = tbl_commu_info.scan(
        ProjectionExpression="communityId,\
                              communityName"
    )
    # ホントはページネーション対応が必要。LastEvaluated
    # communityOwnerはcognito見て名前だずべき

    commu_info_items = scaned_res.get('Items')
    print(commu_info_items)

    commu_weight_keys = []
    for item in commu_info_items:
        key = {
            'communityId': item['communityId'],
            'totalingDate': today
        }
        commu_weight_keys.append(key)

    res_batch_get_item = dynamodb.batch_get_item(
        RequestItems={
            tbl_commu_weight.table_name: {
                'Keys': commu_weight_keys,
                'ProjectionExpression': "communityId,weight"
            }
        }
    )

    commu_weight_items = res_batch_get_item['Responses'][tbl_commu_weight.table_name]
    print(res_batch_get_item)

    df_commu_info = pd.DataFrame(commu_info_items)
    df_commu_weight = pd.DataFrame(commu_weight_items)
    df_commu_joined = pd.merge(df_commu_info, df_commu_weight,
                               on='communityId', how='left')
    commu_list = df_commu_joined.to_dict('records')

    response_data = {
        'items': commu_list
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
        "body": json.dumps(response_data, default=decimal_default_proc)
    }

    return response


def get(event, context):
    # デバッグ用
    print(event)

    query_param = event.get('queryStringParameters')

    community_id = query_param.get('communityId')
    if community_id is None:
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

    tbl_commu_info = dynamodb.Table(os.environ['COMMUNITY_INFO'])
    item: dict = tbl_commu_info.get_item(
        Key={'communityId': community_id},
        ProjectionExpression="communityId,   \
                              communityName, \
                              communityOwner, \
                              content, \
                              createdAt, \
                              updatedAt"
    )

    response_data = {
        'item': item['Item']
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
