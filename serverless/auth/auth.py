import json
import jwt
import os
import boto3

client = boto3.client('cognito-idp')

def auth(event, context):
    data = json.loads(event['body'])

    res_headers = {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Credentials": "true"
    }

    res_auth = None

    try:
        res_auth = client.initiate_auth(
            AuthFlow = "USER_PASSWORD_AUTH",
            ClientId = os.getenv("CLIENT_ID"),
            AuthParameters = {
                'USERNAME': data['email'],
                # FIXME:postデータでpasswordの平文をやり取りしているのは良くない
                'PASSWORD': data['password']
            }
        )
    # TODO:エラーの種類分割。パスワードが一致しませんなど
    except Exception as e:
        print(e)
        response = {
            "header": res_headers,
            "statusCode": 404,
        }
        return response

    access_token = res_auth['AuthenticationResult']["AccessToken"]
    id_token = res_auth["AuthenticationResult"]["IdToken"]
    sub = jwt.decode(id_token,
                     algorithms=["RS256"],
                     options={"verify_signature": False})["sub"]

    try:
        # ユーザーが所属しているコミュ
        user_attrs = client.get_user(AccessToken=access_token).get('UserAttributes')
        commu_id = None
        for attr in user_attrs:
            if attr.get('Name') == 'custom:community_id':
                commu_id = attr['Value']
    # TODO:エラーの種類分割。パスワードが一致しませんなど
    except Exception as e:
        print(e)
        response = {
            "header": res_headers,
            "statusCode": 404,
            "body": str(e)
        }
        return response


    user_info = {
        'accessToken': access_token,
        'idToken': id_token,
        'sub': sub,
        'userBelongCommunityId': commu_id
    }

    response = {
        "statusCode": 200,
        "headers": res_headers,
        "body": json.dumps(user_info)
    }

    return response
