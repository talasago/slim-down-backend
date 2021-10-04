import boto3
import os
from datetime import datetime, timedelta
import pandas as pd
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
if os.getenv('IS_OFFLINE') is not None or \
   os.getenv('AWS_LAMBDA_FUNCTION_NAME') is None:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name="ap-northeast-1",  # localstack用
        endpoint_url="http://localhost:4566",
        aws_access_key_id="DEFAULT_ACCESS_KEY",
        aws_secret_access_key="DEFAULT_SECRET"
    )

table_commu_weight = dynamodb.Table(os.environ['COMMUNITY_WEIGHT'])
table_commu_info = dynamodb.Table(os.environ['COMMUNITY_INFO'])
table_user_weight = dynamodb.Table(os.environ['USER_WEIGHT'])


def weightBatchUpdate(event, context):
    res_scan = table_commu_info.scan(ProjectionExpression='communityId')
    print(res_scan)
    commu_info_items = res_scan['Items']

    today = datetime.now().strftime('%Y%m%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    timestamp = str(datetime.now())

    # レスポンスに LastEvaluatedKey が含まれなくなるまでループ処理を実行
    while 'LastEvaluatedKey' in res_scan:
        res_scan = dynamodb.scan(
            ExclusiveStartKey=res_scan['LastEvaluatedKey'],
            ProjectionExpression='communityId')
        commu_info_items.extend(res_scan['Items'])

    commu_weight_keys = []
    for item in commu_info_items:
        key = item
        key['totalingDate'] = today
        commu_weight_keys.append(key)

    res_batch_get_item = dynamodb.batch_get_item(
        RequestItems={
            table_commu_weight.table_name: {
                'Keys': commu_weight_keys
            }
        }
    )
    commu_weight_items = res_batch_get_item['Responses'][table_commu_weight.table_name]

    df_commu_info = pd.DataFrame(commu_info_items)
    df_commu_weight = pd.DataFrame(commu_weight_items)
    df_commu_joined = pd.merge(df_commu_info, df_commu_weight,
                               on='communityId', how='left')

    put_items = []
    # communityでループ
    for row in df_commu_joined.itertuples():
        today_weight = Decimal(0)

        user_weight_keys = []
        belong_sub_list = []
        # nanの場合は処理しない
        if isinstance(row.belongSubList, list):
            for sub in row.belongSubList:
                user_weight_keys.append({'cognitoUserSub': sub})
                belong_sub_list.append(sub)

        # 集計対象
        if hasattr(row, 'nextTotalingFlg') and \
           row.nextTotalingFlg == "T":
            res_batch_get_item = dynamodb.batch_get_item(
                RequestItems={
                    table_user_weight.table_name: {
                        'Keys': user_weight_keys
                    }
                }
            )

            user_weight_items = res_batch_get_item['Responses'][table_user_weight.table_name]
            weight_sum = Decimal(0)
            for item in user_weight_items:
                weight_sum = item['weight'] + weight_sum
            today_weight = weight_sum
        else:
            # 非集計対象(前日のをコピー)
            item = table_commu_weight.get_item(
                Key={'communityId': row.communityId,
                     'totalingDate': yesterday}
            )
            if item.get('Item') is not None:
                today_weight = item['Item']['weight']
                belong_sub_list = item['Item']['belongSubList']

        put_items.append({
            'PutRequest': {
                'Item': {
                    'communityId': row.communityId,
                    'totalingDate': today,
                    'weight': Decimal(today_weight),
                    'belongSubList': belong_sub_list,
                    'createdAt': timestamp,
                    'updatedAt': timestamp,
                }
            }
        })

    dynamodb.batch_write_item(
        RequestItems={
            table_commu_weight.table_name: put_items
        }
    )

    print('wait_batch_update finished.')
