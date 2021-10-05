import boto3
import os
import datetime

dynamodb = boto3.resource('dynamodb')
if os.getenv('IS_OFFLINE') is not None or \
   os.getenv('AWS_LAMBDA_FUNCTION_NAME') is None:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name="ap-northeast-1",  # localstack
        endpoint_url="http://localhost:4566", # localstack
        aws_access_key_id="DEFAULT_ACCESS_KEY",
        aws_secret_access_key="DEFAULT_SECRET"
    )
table = dynamodb.Table(os.environ['COMMUNITY_WEIGHT'])


class CommunityWeight:
    def __init__(self,
                 community_id,
                 totaling_date,
                 weight=None,
                 next_totaling_flg=None,
                 belong_sub_list=None):
        self.community_id: str = community_id
        self.totaling_date: str = totaling_date
        self.weight: float = weight
        self.next_totaling_flg: str = next_totaling_flg
        self.belong_sub_list: list = belong_sub_list

    # TODO:共通のところをの抜き出す
    def upsert_commu_weight(self, sub: str) -> dict:
        timestamp = str(datetime.datetime.now())

        # sublistを取得してマージする
        res_get = table.get_item(
            Key={
                'communityId': self.community_id,
                'totalingDate': self.totaling_date
            },
            ProjectionExpression="belongSubList"
        )

        if res_get.get('Item') is None:
            sub_list = [sub]
        else:
            sub_list: list = res_get['Item']['belongSubList']
            sub_list.append(sub)
            # 重複要素の削除
            sub_list = list(set(sub_list))

        res_update = table.update_item(
            Key={
                'communityId': self.community_id,
                'totalingDate': self.totaling_date
            },
            ReturnValues='UPDATED_NEW',
            UpdateExpression='SET #flg = :flg, \
                                  #sub_list = :sub_list, \
                                  #time = :time',
            ExpressionAttributeNames={
                '#flg': 'nextTotalingFlg',
                '#sub_list': 'belongSubList',
                '#time': 'updatedAt'
            },
            ExpressionAttributeValues={
                ':flg': 'T',
                ':sub_list': sub_list,
                ':time': timestamp,
            }
        )
        print(res_update)

        return {'massage': "コミュニティに参加しました"}

    def belong_user_leave(self, sub: str) -> dict:
        timestamp = str(datetime.datetime.now())

        # sublistを取得してマージする
        res_get = table.get_item(
            Key={
                'communityId': self.community_id,
                'totalingDate': self.totaling_date
            },
            ProjectionExpression="belongSubList"
        )

        sub_list: list = res_get['Item']['belongSubList']
        # subの削除
        sub_list.remove(sub)

        res_update = table.update_item(
            Key={
                'communityId': self.community_id,
                'totalingDate': self.totaling_date
            },
            ReturnValues='UPDATED_NEW',
            UpdateExpression='SET #flg = :flg, \
                                  #sub_list = :sub_list, \
                                  #time = :time',
            ExpressionAttributeNames={
                '#flg': 'nextTotalingFlg',
                '#sub_list': 'belongSubList',
                '#time': 'updatedAt'
            },
            ExpressionAttributeValues={
                ':flg': 'T',
                ':sub_list': sub_list,
                ':time': timestamp,
            }
        )
        print(res_update)

        return {'massage': "コミュニティから退会しました"}
