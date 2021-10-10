import json
import os
import sys
import boto3
from dotenv import load_dotenv
import pytest
from boto3.session import Session
import configparser
import jwt
# .env読み込み
load_dotenv()

currrent_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(currrent_path, "../"))
# handlerのための環境変数設定
USER_WEIGHT = 'slim-down-user-weight-local'
os.environ['USER_WEIGHT_TABLE'] = USER_WEIGHT
import create
import update
import read

# テストデータ用パラメタ読み込み
config_ini = configparser.ConfigParser()
path_ini = os.path.join(currrent_path, "tests_data/test_weight_param.ini")
config_ini.read(path_ini, encoding='utf-8')

session = Session(profile_name=config_ini['AWS']['AWS_PROFILE'])
client_cip = session.client('cognito-idp')
dynamodb = boto3.resource(
    'dynamodb',
    region_name="ap-northeast-1",  # localstack用
    endpoint_url="http://localhost:4566",
    aws_access_key_id="DEFAULT_ACCESS_KEY",
    aws_secret_access_key="DEFAULT_SECRET"
)
community_weight = dynamodb.Table(USER_WEIGHT)


@pytest.fixture(scope='session')
def auth():
    res_auth = client_cip.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        ClientId=os.getenv("cognitoClientId"),
        AuthParameters={
            'USERNAME': config_ini['auth']['USERNAME'],
            'PASSWORD': config_ini['auth']['PASSWORD']
        }
    )
    return res_auth

@pytest.fixture(scope='session')
def sub_in_token(auth):
    print(auth['AuthenticationResult'])
    decoded_token = jwt.decode(auth['AuthenticationResult']['IdToken'], algorithms=["RS256"],
               options={"verify_signature": False})
    return decoded_token['sub']


def test_create_200(auth, sub_in_token):
    body = {
        'sub': sub_in_token,
        # APIではstrを想定
        'weight': '123.45',
    }
    event = {
        'body': json.dumps(body),
        'headers': {'Authorization': auth['AuthenticationResult']['IdToken']}
    }

    res = create.create(event, '')
    assert res['statusCode'] == 200


def test_update_200(sub_in_token):
    body = {
        'sub': sub_in_token,
        'weight': '123.45',
    }
    event = {
        'body': json.dumps(body),
    }

    res = update.update(event, '')
    assert res['statusCode'] == 200


def test_read_200(sub_in_token):
    event = {
        'queryStringParameters': {
            'sub': sub_in_token
        }
    }

    res = read.get(event, '')
    assert res['statusCode'] == 200
