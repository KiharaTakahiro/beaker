# -*- coding: utf-8 -*-

from flask import Flask, session as session_by_flask, request as request_by_flask, render_template as render_template_by_flask
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta

from common.db import DbConnecter, Transaction
from .utility import load_yaml
import logging.config

class BeakerConfig():
  """Beaker用のConfig定義クラス
  """
  def __init__(self, config_file_name="./config.yml"):
    """Beaker用のConfig定義クラスのコンストラクタ

    Args:
        config_file_name (str, optional): Configファイルのパス. Defaults to "./config.yml".
    """
    self._config = load_yaml(config_file_name)

  def get_config(self):
    """Configの辞書結果を返却する

    Returns:
        dict: Configを辞書形式で返却
    """
    return self._config

_beaker_config = BeakerConfig()
def get_config():
  """Configに設定した配列の取得

  Returns:
      configファイルの配列: Configファイルの配列
  """
  return _beaker_config.get_config()

class BeakerLogLevel():
  """ログレベル設定用のクラス
  """
  DEBUG = 10
  INFO = 20
  WARNING = 30
  ERROR = 40
class BeakerLogger():
  """Beaker用のログ管理クラス
  """
  def __init__(self, config, logger_name="app_logger"):
    """Beakerのログ管理クラスのコンストラクタ

    Args:
        config (BeakerConfig): Beaker用のConfig定義クラス
    """
    logging.config.dictConfig(config['log'])
    self._logger = logging.getLogger(logger_name)

  def log(self, msg, log_level):
    """ログレベルに応じたログ出力

    Args:
        msg (str): エラーメッセージ
        log_level (BeakerLogLevel): Beaker用のログレベル

    Raises:
        Exception: [description]
    """
    if BeakerLogLevel.DEBUG == log_level:
      self.debug(msg)
    elif BeakerLogLevel.INFO == log_level:
      self.info(msg)
    elif BeakerLogLevel.WARNING == log_level:
      self.warning(msg)
    elif BeakerLogLevel.ERROR == log_level:
      self.error(msg)
    else:
      raise Exception(f"存在しないログレベルです。log_level: {log_level}")

  def debug(self, msg):
    """デバッグログの出力

    Args:
        msg (str): 出力メッセージ
    """
    self._logger.debug(msg)

  def info(self, msg):
    """インフォログの出力

    Args:
        msg (str): 出力メッセージ
    """
    self._logger.info(msg)

  def warning(self, msg):
    """警告ログの出力

    Args:
        msg (str): 出力メッセージ
    """
    self._logger.warning(msg)

  def error(self, msg):
    """エラーログの出力

    Args:
        msg (str): 出力メッセージ
    """
    self._logger.error(msg)


logger = BeakerLogger(get_config())

def get_session(key):
  """セッションの値取得処理

  Args:
      key (str): セッションのキー

  Returns:
      str: セッションの値 
  """
  logger.debug(f"キー: {key}")

  if key not in session_by_flask:
    logger.error(f"セッション: {session_by_flask}")
    logger.error(f"キー: {key}")
    raise KeyError("存在しないセッションのキーに対してアクセスしました。")

  return session_by_flask[key]

def set_session(key, value):
  """ セッションの値設定処理

    Args:
      key (str): セッションのキー
      value (str): セッションの値
  """
  logger.debug(f"キー: {key}")
  logger.debug(f"値: {value}")
  session_by_flask[key] = value

def render_template(template_name_or_list, **context):
  """Beaker用テンプレート表示処理

  Args:
      template_name_or_list (str): テンプレート名

  Returns:
      Any: Flaskのテンプレート
  """
  logger.debug(f"テンプレート名: {template_name_or_list}")
  logger.debug(f"コンテキスト: {context}")
  return render_template_by_flask(template_name_or_list, **context)

class BeakerRouter():
  def __init__(self):
    self._route = []

  def get(self, path, function):
    self._route.append({'path': path, 'function': function, 'methods': ['GET',]})

  def post(self, path, function):
    self._route.append({'path': path, 'function': function, 'methods': ['POST',]})

  def regist_flask(self, app):
    """Flaskへの登録処理

    Args:
        app (Flask): ルートの登録対象のflask

    """
    for route in self._route:
      app.add_url_rule(route['path'], view_func=route['function'], methods=route['methods'])

class Beaker():
  """Beaker
     Flaskを拡張してWEBを作成しやすく拡張する
  """
  def __init__(self):

    # コンフィグの読み込み
    app_vars = get_config()['app']
    logger.debug(f"コンフィグ情報: {app_vars}")

    # flaskのappを生成
    # TODO: 今のモジュール配置位置でうまく動かすために下記のようにtemplate_folderを変更しているが 
    #       あるべきではないので配置場所も含めて検討する
    self.__flask = Flask(__name__, template_folder='../templates', static_folder='../statics')
  
    # CSRFトークン設定
    csrf = CSRFProtect(self.__flask)
    self.__flask.config['SECRET_KEY'] = app_vars['secretKey']

    # セッション関連処理
    self.__flask.permanent_session_lifetime = timedelta(minutes=app_vars['sessionTimeoutMinutes'])
    self.__flask.secret_key = app_vars['secretKey']
    
    # NOTE: 30分おきにログインするのはつらいのでリクエストがあった場合にセッションを延命する
    # 常にログインまでの時間としたい場合はこの処理をコメントアウトする
    self.before_request(self._extension_session)

    # リクエストの内容をログ出力する処理をかませる
    self.before_request(self._request_logger)

    # route定義をインポート
    # NOTE: 循環参照を防ぐためここでインポートする
    from web import router
    router.regist_flask(self.__flask)

  def before_request(self, function):
    """リクエスト実行前のロジックを格納する

    Args:
        function (f)): リクエストに追加するファンクションを設定する
    """
    self.__flask.before_request(function)

  def _extension_session(self):
    """セッションを延命する
    """
    session_by_flask.permanent = True
    self.__flask.permanent_session_lifetime = timedelta(minutes=get_config()['app']['sessionTimeoutMinutes'])
    session_by_flask.modified = True

  def _request_logger(self):
    """リクエストの内容をログ出力
    """
    logger.debug(f"セッション情報: {session_by_flask}")
    logger.debug(f"リクエスト情報: {request_by_flask}")

  def run(self):
    self.__flask.run(port=get_config()['app']['port'])

class BeakerDB():
  def __init__(self, config, logger):
    """Beaker用DBの使用クラス

    Args:
        config (BeakerConfig): Beakerのコンフィグ用クラス
        logger (BeakerLogger): Beakerのログ用クラス
    """
    self._logger = logger

    db_info = config['database']
    self._logger.debug(f"dbの接続情報: {db_info}")

    self._connector = DbConnecter(
      db_info['dbname'], \
      db_info['host'],\
      db_info['user'],\
      db_info['password'])
  
  def start_transaction(self, read_only = True):
    """トランザクション開始処理

    Args:
        read_only (bool, optional): 読み込み専用か？ 読み込み専用の場合はTrueとなりコミットを行わない. Defaults to True.

    Returns:
        Transaction: トランザクションを返却する
    """
    return Transaction(self._connector, self._logger, read_only)

_beaker_db = BeakerDB(get_config(), logger)
def start_transaction(read_only = True):
  """トランザクション開始処理

  Args:
      read_only (bool, optional): 読み込み専用か？ 読み込み専用の場合はTrueとなりコミットを行わない. Defaults to True.

  Returns:
      Transaction: トランザクションを返却する
  """
  return _beaker_db.start_transaction(read_only=read_only)

request = request_by_flask
