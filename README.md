# BEAKERの概要
flaskを拡張していつも設定するような内容を事前に設定できるようにまとめるとともにLaravelから入ってきたエンジニアがflaskにとっつきやすくなるようにrouterの定義をLaravelのweb.phpでの設定と似たような方法で設定できるように変更しました。

# 前提
[poetry](https://cocoatomo.github.io/poetry-ja/)を使用しておりますので各自インストールをお願いします。
pipの場合は下記のコマンドでインストール可能です。(--userは必要であれば使ってください)
```
pip install --user poetry
```
データベースはpostgresの使用を想定しています。各自postgresのインストールをお願いします。

# クイックスタート(Windows)
## 初回のみ実施が必要なこと
1. [example.config.yml](https://github.com/KiharaTakahiro/beaker/blob/main/example.config.yml)をもとにconfig.ymlを作成(とりあえず試すだけならばリネームでOK)
1. beakerディレクトリで`poertry install`を実行しpoetryでの実行ができるようにする
## 起動時に必要なこと
1. beakerディレクトリで`poertry shell`を実行しpoetryでの実行ができるようにする
1. `cd beaker`にてbeakerにディレクトリを移動
1. `python app.py`にてbeakerを実行
1. [http://127.0.0.1:5000/](http://127.0.0.1:5000/)にアクセスするとwelcomeページが表示される

# 使い方
## ルート定義設定
### [web.py](https://github.com/KiharaTakahiro/beaker/blob/main/web.py)にてrouterの設定を行う
```python: web.py
# routerのインポート
from common.beaker import BeakerRouter
router = BeakerRouter()

from controllers.welcome_controller import welcome, welcome_post

# ルート定義の設定
# GETさせたい場合はrouter.get(endpoint, function)となるように記載する
router.get('/', welcome)
# POSTさせたい場合はrouter.post(endpoint, function)となるように記載する
router.post('/welcome_post', welcome_post)

```
### routerで指定した処理を記載する
```python: test_controller.py
from common.beaker import render_template # beakerでrender_templateが使えます

def welcome():
  # flaskのrender_templateと同様の方法をbeakerから使用できる(bakerのrender_templateを使用すればデバッグログで実行内容が出力されます)
  return render_template('welcome.html')
```

## CSRFトークン
デフォルトではCSRFトークンがない場合はPOST時にエラーとなります。
下記のようにFormにCSRFトークンを含めてください。
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```
※細かく記載するのを省略しますが、内部は[CSRF Protection](https://flask-wtf.readthedocs.io/en/0.15.x/csrf/)を使用しているのでForm以外で使用している場合もドキュメントに沿ってCSRFトークンを含めていただければと思います。

## ログ出力
loggerをインポートしてそれぞれのメソッドを呼び出すことでログ出力が可能になります。
```
from common.beaker import logger

def log_test():
  logger.debug('debugログの出力')
  logger.info('infoログの出力')
  logger.warning('warningログの出力')
  logger.error('errorログの出力')

```

## セッションの使用
セッションを使用することができます。
下記のメソッドを使用して設定および取得を行ってください。
```
from common.beaker import get_session, set_session

def session_test():
  # セッションの設定
  set_session('key', 'value')
  
  # セッションの取得
  session_value = get_session('key')

```
## SQLの実行
SQLの実行はstart_transactionを使用して実行できます。
### 取得系のSQL(SELECT文の場合)
```python
from common.beaker import start_transaction

def execute_sql():
  with start_transaction() as tx:
    # 複数行取得の場合
    users = tx.find_all({実行するSQL})
    # 最初の一件目取得の場合
    user = tx.find_one({実行するSQL})
```

### 更新系のSQL(INSERT, UPDATE文の場合)
```python
from common.beaker import start_transaction

def execute_sql():
  with start_transaction(read_only = False) as tx:
    tx.save({実行するSQL})

```

### 削除系のSQL(DELETE文の場合)
```python
from common.beaker import start_transaction

def execute_sql():
  with start_transaction(read_only = False) as tx:
    tx.delete({実行するSQL})

```
※ロジック上はsaveでも削除系のSQLの実行は可能だが、今後の拡張も考えて削除時に実行するSQLは分けることを推奨します。

## クエリビルダ
### 取得
下記のコードで該当抽出条件に従ってSQLが生成されます
#### 書き方
```
# サンプル
  with start_transaction() as tx:
    query_builder = create_query_builder(tx)
    client = query_builder.table('{テーブル名}').where('{フィールド名}', '=', 2).or_where('{フィールド名2}', '=', 3).select()

# 全項目を取得する必要がない時はselectの引数に与えれば必要分だけの取得になります
client = query_builder.table('{テーブル名}').where('{フィールド名}', '=', 2).or_where('{フィールド名2}', '=', 3).select('{フィールド名3}',{フィールド名4})
```

#### 生成されるSQL
`SELECT * FROM {テーブル名} WHERE {フィールド名} = %s OR {フィールド名2} = %s;`
AND条件としたいときはwhereを続けて使用すればAND条件となります

### 登録
登録内容に従ってINSERT文を発行します。
#### 書き方
```
  with start_transaction(False) as tx:
    query_builder = create_query_builder(tx)
    query_builder.table('{テーブル名}').insert({'{フィールド名}': 6, '{フィールド名2}': 'test'})

```
#### 生成されるSQL文
`INSERT INTO {テーブル名} ({フィールド名}, {フィールド名2}) VALUES (%s, %s);`

### 更新
更新内容に従って更新処理を行います。
#### 書き方
```
  with start_transaction(False) as tx:
    query_builder = create_query_builder(tx)
    query_builder.table('{テーブル名}').where('{フィールド名}', '=', 6).update({'{フィールド名2}': 'test2'})

```
#### 生成されるSQL文
`UPDATE {テーブル名} SET {フィールド名2} = %s WHERE {フィールド名}= %s;`

### 削除
下記の内容に従って削除処理を行います。
#### 書き方
```
  with start_transaction(False) as tx:
    query_builder = create_query_builder(tx)
    query_builder.table('{テーブル名}').where('{フィールド名}', '=', 6).delete()
```
#### 生成されるSQL文
`DELETE FROM {テーブル名} WHERE {フィールド名}= %s;`

## カスタムフィルタの追加について
[template_filters.py](https://github.com/KiharaTakahiro/beaker/blob/main/template_filters.py)に記載されたメソッドはtemplateで同名のカスタムフィルタが使用可能になります。
### template_filters.pyにてカスタムフィルタを追加する（例は金額変換処理）
```
from common.beaker import logger

def convert_money(number, is_none_text = '0'):
  """3桁カンマ区切りの金額に変換する処理
     例) 10000 → 10,000

     注意点) 小数点は未対応のため必要な場合は別のメソッドを作成して対応する
  Args:
      number (number): カンマ区切りにする数値 
      is_none_text (str, optional): numberがNoneの場合の置き換え文字列. Defaults to '0'.

  Returns:
      str: 3桁カンマ区切りの金額を返却
  """
  # 対象がNoneの場合は置き換えようの文字列を返却
  if number is None:
    return is_none_text

  try:
    logger.debug(f'3桁カンマ区切り処理のnumber: {number}')

    # 3桁カンマ区切りの文字列を返却
    return '{:,}'.format(int(number))

  except Exception:
    # HACK: 全体的に表示に関わる部分でエラーにしないようにしたほうが良いと考えて元文字列の返却を行っている
    #       運用の中でエラーの発見を起こすリスクも考えた上で再度検討しても良いと考えている
    logger.warning(f'3桁カンマ区切り処理に失敗しています number: {number}')
    return number
```
### template内で以下のように指定して使用が可能
```
# 通常の使い方で第一引数に1000として関数が実行された結果が返ってくる
{{ 1000 | convert_money }}

# 第二引数以降を使いたい場合は以下のようにする
{{ None | convert_money('-') }}

# キーワード引数も使用可能
{{ None | convert_money(is_none_text'-') }}
```
