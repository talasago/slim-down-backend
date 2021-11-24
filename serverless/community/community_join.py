import json
from models.community_weight import CommunityWeightRepository
import datetime
import os
import boto3
from boto3.session import Session


client_cip = boto3.client('cognito-idp')
if os.getenv('IS_OFFLINE') is not None or \
   os.getenv('AWS_LAMBDA_FUNCTION_VERSION') is None:
    session = Session(profile_name=os.getenv('AWS_PROFILE'))
    client_cip = session.client('cognito-idp')


def community_join(event, context):
    # for debug
    print(event)

    data = json.loads(event['body'])
    community_id: str = data.get('communityId')
    sub: str = data.get('sub')
    access_token: str = event['headers']['Authorization']

    if community_id is None or\
       sub is None or \
       access_token is None:

        if community_id is None:
            massage = 'コミュニティIDは必須です。'
        if sub is None:
            massage += 'subは必須です。'
        if access_token is None:
            massage += 'コミュニティIDは必須です。'

        response_data = {
            'massage': massage
        }

        response = {
            "statusCode": 400,
            'headers': {
                "Content-type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "PUT",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date, \
                    Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Credentials": "true"
            },
            "body": json.dumps(response_data)
        }
        return response

    today = datetime.datetime.now()
    totaling_date = today.strftime('%Y%m%d')

    try:
        cw = CommunityWeightRepository.find_by(community_id, totaling_date)
        if cw is None:
            raise LookupError('communityWeightテーブルにレコードが存在しません')
        cw.sub_add(sub)
        cw.next_totaling_flg = 'T'
        cw.update_item()
        response_data = {'massage': "コミュニティに参加しました"}
    except Exception as e:
        response = {
            "statusCode": 500,
            'headers': {
                "Content-type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "PUT",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date, \
                    Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Credentials": "true"
            },
            "body": {"massage": json.dumps(str(e))}
        }
        return response

    # TODO:エラー処理
    response = client_cip.update_user_attributes(
        UserAttributes=[{
            'Name': 'custom:community_id',
            'Value': community_id
        }],
        AccessToken=access_token,
    )

    response = {
        "statusCode": 200,
        'headers': {
            "Content-type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date, \
                Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(response_data)
    }

    return response
