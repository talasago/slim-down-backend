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
        self.__next_totaling_flg: str = next_totaling_flg
        self.__belong_sub_list: str = belong_sub_list

    @property
    def belong_sub_list(self):
        return self.__belong_sub_list

    @belong_sub_list.setter
    def belong_sub_list(self, belong_sub_list):
        self.__belong_sub_list = belong_sub_list

    @property
    def next_totaling_flg(self):
        return self.__next_totaling_flg

    @next_totaling_flg.setter
    def next_totaling_flg(self, next_totaling_flg):
        self.__next_totaling_flg = next_totaling_flg

    def sub_add(self, sub: str):

        if self.belong_sub_list is None:
            sub_list = [sub]
        else:
            sub_list: list = self.belong_sub_list
            sub_list.append(sub)
            # 重複要素の削除
            sub_list = list(set(sub_list))
        self.belong_sub_list = sub_list

    def sub_remove(self, sub: str):
        sub_list: list = self.belong_sub_list
        # subの削除
        sub_list.remove(sub)
        self.belong_sub_list = sub_list

    def update_item(self):
        timestamp = str(datetime.datetime.now())

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
                ':flg': self.next_totaling_flg,
                ':sub_list': self.belong_sub_list,
                ':time': timestamp,
            }
        )
        print(res_update)


class CommunityWeightRepository:
    def find_by(community_id: str, totaling_date: str) -> CommunityWeight:
        # sublistを取得してマージする
        res_get = table.get_item(
            Key={
                'communityId': community_id,
                'totalingDate': totaling_date
            },
            ProjectionExpression="belongSubList"
        )

        cw = CommunityWeight(
            community_id,
            totaling_date,
            weight=res_get['Item'].get('weight'),
            next_totaling_flg=res_get['Item'].get('nextTotalingFlg'),
            belong_sub_list=res_get['Item'].get('belongSubList')
        )

        return cw
