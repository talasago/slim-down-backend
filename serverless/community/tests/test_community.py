from unittest import TestCase
from dotenv import load_dotenv
import json
import os
import sys
import boto3
import datetime
from boto3.session import Session
import configparser

currrent_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(currrent_path, "../"))

COMMUNITY_WEIGHT = 'slim-down-community-weight-local'
os.environ['COMMUNITY_INFO'] = 'slim-down-community-info-local'
os.environ['COMMUNITY_WEIGHT'] = COMMUNITY_WEIGHT
import create  # noqa: E402
import read    # noqa: E402
import update  # noqa: E402
import delete  # noqa: E402
import comunity_join  # noqa: E402
load_dotenv()

session = Session(profile_name=os.getenv('AWS_PROFILE'))
client_cip = session.client('cognito-idp')
dynamodb = boto3.resource(
    'dynamodb',
    region_name="ap-northeast-1",  # localstack用
    endpoint_url="http://localhost:4566",
    aws_access_key_id="DEFAULT_ACCESS_KEY",
    aws_secret_access_key="DEFAULT_SECRET"
)
community_weight = dynamodb.Table(COMMUNITY_WEIGHT)

config_ini = configparser.ConfigParser()
path_ini = os.path.join(currrent_path, "tests-data/test_community.ini")
config_ini.read(path_ini, encoding='utf-8')


def test_create_200():
    body = {
        'communityId': 'test_commu2',
        'communityName': 'テストコミュニティ名',
        'communityOwnerSub': 'community_owner_sub',
        'content': 'これは\nコミュニティ情報作成のテストです'
    }
    event = {'body': json.dumps(body)}

    res = create.create(event, '')
    assert res['statusCode'] == 200


def test_get_list_200():
    expexted_body = {
        'communityId': 'test_commu2',
        'communityName': 'テストコミュニティ名',
        'communityOwnerSub': 'community_owner_sub',
        'content': 'これは\nコミュニティ情報作成のテストです'
    }
    res = read.get_list('', '')
    res_body = json.loads(res['body'])
    assert res['statusCode'] == 200
    # ホントはうまいことdictを比較したい
    assert res_body['items'][0]['communityId'] == expexted_body['communityId']


def test_get_200():
    expexted_body = {
        'communityId': 'test_commu2',
        'communityName': 'テストコミュニティ名',
        'communityOwnerSub': 'community_owner_sub',
        'content': 'これは\nコミュニティ情報作成のテストです'
    }
    event = {
        'queryStringParameters': {
            'communityId': 'test_commu2'
        }
    }
    res = read.get(event, '')
    res_body = json.loads(res['body'])

    assert res['statusCode'] == 200
    assert res_body['item']['communityId'] == expexted_body['communityId']


def test_update_200():
    body = {
        'communityId': 'test_commu2',
        'communityName': 'テストコミュニティXXX',
        'content': 'This is \n community-info'
    }
    event = {'body': json.dumps(body)}

    res = update.update(event, '')
    res_body = json.loads(res['body'])

    assert res['statusCode'] == 200
    assert res_body['communityName'] == body['communityName']


def test_delete_200():
    body = {
        'communityId': 'test_commu2',
    }
    event = {'body': json.dumps(body)}

    res = delete.delete(event, '')

    assert res['statusCode'] == 200


def test_community_join_200():
    res_auth = client_cip.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        ClientId=os.getenv("cognitoClientId"),
        AuthParameters={
            'USERNAME': config_ini['auth']['USERNAME'],
            'PASSWORD': config_ini['auth']['PASSWORD']
        }
    )

    access_token = res_auth['AuthenticationResult']["AccessToken"]

    body = {
        'communityId': 'test_commu2',
        'sub': '76e6f480-5f0a-4863-97f8-aff844774a5c'
    }

    event = {
        'headers': {'Authorization': {
            'AccessToken': access_token
        }},
        'body': json.dumps(body)
    }

    res = comunity_join.community_join(event, '')
    assert res['statusCode'] == 200

    today = datetime.datetime.now()
    totaling_date = today.strftime('%Y%m%d')
    item: dict = community_weight.get_item(
        Key={
            'communityId': body['communityId'],
            'totalingDate': totaling_date
        },
        ProjectionExpression="communityId,   \
                              totalingDate, \
                              nextTotalingFlg, \
                              belongSubList"
    )
    actual_sub_list = item['Item']['belongSubList']
    assert body['sub'] in actual_sub_list

    user = client_cip.get_user(
        AccessToken=access_token
    )
    attrs = user['UserAttributes']
    for attr in attrs:
        if attr['Name'] == 'custom:community_id':
            exsist_flg = True
            assert attr['Value'] == body['communityId']
    assert exsist_flg
