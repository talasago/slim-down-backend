import json
from models.community_weight import CommunityWeight, CommunityWeightRepository
import datetime
import os
from dotenv import load_dotenv
import boto3
from boto3.session import Session

load_dotenv()

client_cip = boto3.client('cognito-idp')
if os.getenv('IS_OFFLINE') is not None or \
   os.getenv('AWS_LAMBDA_FUNCTION_VERSION') is None:
    session = Session(profile_name=os.getenv('AWS_PROFILE'))
    client_cip = session.client('cognito-idp')


def community_leave(event, context):
    # for debug
    print(event)

    data = json.loads(event['body'])
    community_id: str = data.get('communityId')
    sub: str = data.get('sub')
    access_token: str = event['headers']['Authorization']['AccessToken']

    if community_id is None or\
       sub is None or \
       access_token is None:

        if community_id is None:
            massage = 'コミュニティIDは必須です。'
        if sub is None:
            massage += 'subは必須です。'

        response_data = {
            'massage': massage
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

    today = datetime.datetime.now()
    totaling_date = today.strftime('%Y%m%d')

    try:
        cw = CommunityWeightRepository.find_by(community_id, totaling_date)
        cw.sub_remove(sub)
        cw.next_totaling_flg = 'T'
        cw.update_item()
        response_data = {'massage': "コミュニティから退会しました"}
    except Exception as e:
        response = {
            "statusCode": 500,
            'headers': {
                "Content-type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "1",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date, \
                    Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Credentials": "true"
            },
            "body": {"massage": str(e)}
        }
        return response

    response = client_cip.delete_user_attributes(
        UserAttributeNames=[
            'custom:community_id'
        ],
        AccessToken=access_token,
    )

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
