# 環境構築手順
```Bash
#各ディレクトリで設定が必要
npm config set prefix '../'

# 親ディレクトリではなく、カレントディレクトリpipenvを使う
# カレントディレクトリに仮想環境を作る
export PIPENV_NO_INHERIT=True;export PIPENV_VENV_IN_PROJECT=True;
## 初期なら
pipenv install --python 3.8.11
## cloneしたら
pipenv install
## ユニットテスト起動
pipenv run pytest 
```


## 旧:ローカル起動
sls offline --stage dev --printOutput
sls dynamodb start

## 注意事項
dynamodbはデプロイするたびに削除が必要。
deploy時にすでにtableが存在する場合はエラーとなる。
