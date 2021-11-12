#!/bin/bash

# テーブル作成
awslocal dynamodb create-table --table-name 'slim-down-community-info-local' \
--attribute-definitions '[{"AttributeName":"communityId","AttributeType": "S"}]' \
--key-schema '[{"AttributeName":"communityId","KeyType": "HASH"}]' \
--provisioned-throughput '{"ReadCapacityUnits": 1,"WriteCapacityUnits": 1}' || true

# レコードが多くなりすぎるので一旦削除
awslocal dynamodb delete-table --table-name 'slim-down-community-weight-local'

awslocal dynamodb create-table --table-name 'slim-down-community-weight-local' \
--attribute-definitions '[{"AttributeName":"communityId","AttributeType": "S"},{"AttributeName":"totalingDate","AttributeType": "S"},{"AttributeName":"nextTotalingFlg","AttributeType": "S"}]' \
--key-schema '[{"AttributeName":"communityId","KeyType": "HASH"},{"AttributeName":"totalingDate","KeyType": "RANGE"}]' \
--provisioned-throughput '{"ReadCapacityUnits": 1,"WriteCapacityUnits": 1}' \
--global-secondary-indexe \
        '[{"IndexName": "index-nextTotalingFlg",
            "KeySchema": [{"AttributeName":"nextTotalingFlg","KeyType":"HASH"}],
            "Projection": {"ProjectionType":"ALL"},
            "ProvisionedThroughput": {"ReadCapacityUnits": 1,"WriteCapacityUnits": 1}
        }]' || true

awslocal dynamodb create-table --table-name 'slim-down-user-weight-local' \
--attribute-definitions '[{"AttributeName":"cognitoUserSub","AttributeType": "S"}]' \
--key-schema '[{"AttributeName":"cognitoUserSub","KeyType": "HASH"}]' \
--provisioned-throughput '{"ReadCapacityUnits": 1,"WriteCapacityUnits": 1}' || true

# テストデータを読み込み
awslocal dynamodb put-item --table-name 'slim-down-community-info-local' \
    --cli-input-json file:///docker-entrypoint-initaws.d/dynamodb/community-info.json || ture
awslocal dynamodb put-item --table-name 'slim-down-community-info-local' \
    --cli-input-json file:///docker-entrypoint-initaws.d/dynamodb/community-info2.json || true
awslocal dynamodb put-item --table-name 'slim-down-community-info-local' \
    --cli-input-json file:///docker-entrypoint-initaws.d/dynamodb/community-info3.json || true


today="$(date +%Y%m%d)"
input_param=$(sed "s/###TODAY###/${today}/g" /docker-entrypoint-initaws.d/dynamodb/community-weight.json)
awslocal dynamodb put-item --table-name 'slim-down-community-weight-local' \
    --cli-input-json "${input_param}" || true

today="$(date +%Y%m%d)"
input_param=$(sed "s/###TODAY###/${today}/g" /docker-entrypoint-initaws.d/dynamodb/community-weight2.json)
awslocal dynamodb put-item --table-name 'slim-down-community-weight-local' \
    --cli-input-json "${input_param}" || true
