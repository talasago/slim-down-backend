import json
# import requests
import os
import sys

currrent_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(currrent_path, "../"))
os.environ['COMMUNITY_INFO'] = 'slim-down-community-info-dev'
import create  # noqa: E402
import read    # noqa: E402
import update  # noqa: E402


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
