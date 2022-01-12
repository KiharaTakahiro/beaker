# BEAKERの概要
flaskを拡張していつも設定するような内容を事前に設定できるようにまとめるとともにLaravelから入ってきたエンジニアがflaskにとっつきやすくなるようにrouterの定義をLaravelのweb.phpでの設定と似たような方法で設定できるように変更しました。

# クイックスタート(Windows)
1. [example.config.yml](https://github.com/KiharaTakahiro/beaker/blob/main/example.config.yml)をもとにconfig.ymlを作成(とりあえず試すだけならばリネームでOK)
1. `python app.py`にてbeakerを実行
1. [http://127.0.0.1:5000/](http://127.0.0.1:5000/)にアクセスするとwelcomeページが表示される

# 使い方
## web.pyにてrouterの設定を行う
```python: web.py
# routerのインポート
from common.beaker import BeakerRouter
router = BeakerRouter()

# ルート定義の設定
# GETさせたい場合はrouter.get(endpoint, function)となるように記載する
from controllers.welcome_controller import welcome
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
