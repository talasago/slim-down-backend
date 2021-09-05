
import json
# import requests
import os
import sys
currrent_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(currrent_path, "../"))
os.environ['COMMUNITY_INFO'] = 'slim-down-community-info-dev'
import create  # noqa: E402


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
        'community_id': 'test_commu',
        'community_name': 'テストコミュニティ名',
        'community_owner_sub': 'community_owner_sub',
        'content': 'これは\nコミュニティ情報作成のテストです'
    }
    event = {'body': json.dumps(body)}

    res = create.create(event, '')
    assert res['statusCode'] == 200
