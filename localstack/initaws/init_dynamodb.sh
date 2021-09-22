#!/bin/bash

# テーブル作成
awslocal dynamodb create-table --table-name 'slim-down-community-info-local' \
--attribute-definitions '[{"AttributeName":"communityId","AttributeType": "S"}]' \
--key-schema '[{"AttributeName":"communityId","KeyType": "HASH"}]' \
--provisioned-throughput '{"ReadCapacityUnits": 1,"WriteCapacityUnits": 1}'

awslocal dynamodb create-table --table-name 'slim-down-community-weight-local' \
--attribute-definitions '[{"AttributeName":"communityId","AttributeType": "S"},{"AttributeName":"totalingDate","AttributeType": "S"},{"AttributeName":"nextTotalingFlg","AttributeType": "S"}]' \
--key-schema '[{"AttributeName":"communityId","KeyType": "HASH"},{"AttributeName":"totalingDate","KeyType": "RANGE"}]' \
--provisioned-throughput '{"ReadCapacityUnits": 1,"WriteCapacityUnits": 1}' \
--global-secondary-indexe \
        '[{"IndexName": "index-nextTotalingFlg",
            "KeySchema": [{"AttributeName":"nextTotalingFlg","KeyType":"HASH"}],
            "Projection": {"ProjectionType":"ALL"},
            "ProvisionedThroughput": {"ReadCapacityUnits": 1,"WriteCapacityUnits": 1}
        }]'

awslocal dynamodb create-table --table-name 'slim-down-user-weight-local' \
--attribute-definitions '[{"AttributeName":"cognitoUserSub","AttributeType": "S"}]' \
--key-schema '[{"AttributeName":"cognitoUserSub","KeyType": "HASH"}]' \
--provisioned-throughput '{"ReadCapacityUnits": 1,"WriteCapacityUnits": 1}'

# テストデータを読み込み
awslocal dynamodb put-item --table-name 'slim-down-community-info-local' \
    --cli-input-json file:///docker-entrypoint-initaws.d/dynamodb/community-info.json

awslocal dynamodb put-item --table-name 'slim-down-community-info-local' \
    --cli-input-json file:///docker-entrypoint-initaws.d/dynamodb/community-info2.json
