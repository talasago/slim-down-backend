import json
# import requests
import os
import sys

currrent_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(currrent_path, "../"))
os.environ['COMMUNITY_INFO'] = 'slim-down-community-info-dev'
import create  # noqa: E402
import read    # noqa: E402

#def test_create_200_api():
#    payload = {
#        'community_id': 'test_commu',
#        'community_name': 'テストコミュニティ名',
#        'community_owner_sub': 'community_owner_sub',
#        'content': 'これは\nコミュニティ情報作成のテストです'
#    }
#    res = requests.post('http://localhost:3000/dev/community/info',
#                        data=json.dumps(payload))
#
#    # res = create.create(event, '')
#    assert res['statusCode'] == 200


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
