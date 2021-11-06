from decimal import Decimal
import os
import sys
import boto3
import pytest
from datetime import datetime, timedelta

currrent_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(currrent_path, "../"))
os.environ['COMMUNITY_INFO'] = 'slim-down-community-info-local'
os.environ['COMMUNITY_WEIGHT'] = 'slim-down-community-weight-local'
os.environ['USER_WEIGHT'] = 'slim-down-user-weight-local'
import weight_batch_update # noqa E402

dynamodb = boto3.resource(
    'dynamodb',
    region_name="ap-northeast-1",  # localstack用
    endpoint_url="http://localhost:4566",
    aws_access_key_id="DEFAULT_ACCESS_KEY",
    aws_secret_access_key="DEFAULT_SECRET"
)
community_weight = dynamodb.Table('slim-down-community-weight-local')
user_weight = dynamodb.Table('slim-down-user-weight-local')

today = datetime.now().strftime('%Y%m%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')


@pytest.fixture()
def init_commu_weight():
    # 先にcommuweightは全削除した方がいいかも
    commu_weight_items = [
        {
            'PutRequest': {
                'Item': {
                    'communityId': 'test-commu-info',
                    'totalingDate': today,
                    'weight': '123.44',
                    'belongSubList': ["aaa", "bbb", "ccc"],
                    'nextTotalingFlg': 'T',
                }
            }
        },
        {
            'PutRequest': {
                'Item': {
                    'communityId': 'test-commu-info2',
                    'totalingDate': yesterday,
                    'weight': '333.4',
                    'belongSubList': ["eee"]
                }
            }
        }
    ]

    user_weigth_items = [
        {
            'PutRequest': {
                'Item': {
                    "cognitoUserSub": "aaa",
                    "weight": Decimal('63.45')
                }
            }
        },
        {
            'PutRequest': {
                'Item': {
                    "cognitoUserSub": "bbb",
                    "weight": Decimal('66.45')
                }
            }
        },
        {
            'PutRequest': {
                'Item': {
                    "cognitoUserSub": "ccc",
                    "weight": Decimal('64.7')
                }
            }
        },
        {
            'PutRequest': {
                "Item": {
                    "cognitoUserSub": "ddd",
                    "weight": Decimal('23.44')
                }
            }
        }
    ]

    dynamodb.batch_write_item(
        RequestItems={
            community_weight.table_name: commu_weight_items,
            user_weight.table_name: user_weigth_items
        }
    )

    # commuweighレコードが存在しないテスト
    community_weight.delete_item(
        Key={
            'communityId': 'test-commu-info3',
            'totalingDate': today
        }
    )
    community_weight.delete_item(
        Key={
            'communityId': 'test-commu-info3',
            'totalingDate': yesterday
        }
    )


def test_weight_batch_update(init_commu_weight):
    weight_batch_update.weight_batch_update('', '')

    item = community_weight.get_item(
        Key={
            'communityId': 'test-commu-info',
            'totalingDate': today
        }
    )
    assert item['Item']['weight'] == Decimal('194.6')

    item = community_weight.get_item(
        Key={
            'communityId': 'test-commu-info2',
            'totalingDate': today
        }
    )
    assert item['Item']['weight'] == Decimal('333.4')

    item = community_weight.get_item(
        Key={
            'communityId': 'test-commu-info3',
            'totalingDate': today
        }
    )
    assert item.get('Item').get('weight') == Decimal('0')
