# BEAKERの概要
flaskを拡張していつも設定するような内容を事前に設定できるようにまとめるとともにLaravelから入ってきたエンジニアがflaskにとっつきやすくなるようにrouterの定義をLaravelのweb.phpでの設定と似たような方法で設定できるように変更しました。

# クイックスタート(Windows)
1. [example.config.yml](https://github.com/KiharaTakahiro/beaker/blob/main/example.config.yml)をもとにconfig.ymlを作成(とりあえず試すだけならばリネームでOK)
1. `python app.py`にてbeakerを実行
1. [http://127.0.0.1:5000/](http://127.0.0.1:5000/)にアクセスするとwelcomeページが表示される
※現時点でパッケージ管理を何にするか決めていないのでモジュール不足でエラーとなった場合は必要なモジュールのインストールをお願いします。


# 使い方
## web.pyにてrouterの設定を行う
```python: web.py
# routerのインポート
from common.beaker import BeakerRouter
router = BeakerRouter()

# ルート定義の設定
# GETさせたい場合はrouter.get(endpoint, function)となるように記載する
from controllers.welcome_controller import welcome, welcome_post
router.get('/', welcome)

# POSTさせたい場合はrouter.post(endpoint, function)となるように記載する 現時点ではロジックが書かれてないので記載しても実行できません
router.post('/', welcome_post)

```
## routerで指定した処理を記載する
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
