# -*- coding: utf-8 -*-

from flask import Flask, session as session_by_flask, request as request_by_flask, render_template as render_template_by_flask, make_response
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta

from .db import DbConnecter, Transaction, QueryBuilder
from .csv import CsvCreator
from .utility import load_yaml
import logging.config
import sys
import inspect

_py2 = sys.version_info[0] == 2
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
    # デフォルトを以下のように定義する
    logger_map =  {
      'version': 1, 
      'formatters': {
        'customFormatter': {
          'format': '[%(asctime)s]%(levelname)s - %(message)s', 
          'datefmt': '%Y/%m/%d %H:%M:%S'
         }
       },
      'loggers': {
        logger_name : {
          'handlers': ['fileRotatingHandler', 'consoleHandler'],
          'level': config['log']['level'],
          'qualname': 'file',
          'propagate': False}},
          'handlers': {
            'fileRotatingHandler': {
              'formatter': 'customFormatter', 
              'class': 'logging.handlers.TimedRotatingFileHandler', 
              'level': config['log']['level'], 
              'filename': config['log']['file_name'], 
              'encoding': 'utf8', 
              'when': 'D', 
              'interval': 1, 
              'backupCount': 14
              }, 
            'consoleHandler': {
              'class': 'logging.StreamHandler', 
              'level': config['log']['level'], 
              'formatter': 'customFormatter', 
              'stream': 'ext://sys.stdout'
              }
            }, 
            'root': {
              'level': config['log']['level']
              }
            }
    logging.config.dictConfig(logger_map)
    self._logger = logging.getLogger(logger_name)

  def _get_file_name(self):
    """ログの出力先の情報を取得する

    Returns:
        tuple: ファイル名と関数名の取得を行う
    """
    # NOTE: 本メソッドは各出力処理から呼ばれているのでstackから2つ
    #       遡ったもの関数がログの出力先であるとする
    file_name = inspect.stack()[2].filename
    function_name = inspect.stack()[2].function
    return (file_name, function_name)

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

  def debug(self, message):
    """デバッグログの出力

    Args:
        message (str): 出力メッセージ
    """
    file_name, function_name = self._get_file_name()
    self._logger.debug(f'{file_name}#{function_name}: {message}')

  def info(self, message):
    """インフォログの出力

    Args:
        message (str): 出力メッセージ
    """
    file_name, function_name = self._get_file_name()
    self._logger.info(f'{file_name}#{function_name}: {message}')

  def warning(self, message):
    """警告ログの出力

    Args:
        message (str): 出力メッセージ
    """
    file_name, function_name = self._get_file_name()
    self._logger.warning(f'{file_name}#{function_name}: {message}')

  def error(self, message):
    """エラーログの出力

    Args:
        message (str): 出力メッセージ
    """
    file_name, function_name = self._get_file_name()
    self._logger.error(f'{file_name}#{function_name}: {message}')

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

  def get(self, path, function, auth=False):
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

def _internal_server_error(e):
  """内部サーバエラーが発生した場合の処理
  """
  logger.error('内部サーバエラーが発生しました。')
  logger.error(e)
  logger.error(f"セッション情報: {session_by_flask}")
  logger.error(f"リクエスト情報: {request_by_flask}")
  return render_template('errors/500.html'), 500

def _page_not_found(e):
  """404エラーが発生した場合の処理

  Returns:
      Any: 404エラーが発生した場合のテンプレートを変更する
  """
  logger.error('404エラーが発生しました。')
  logger.error(f"リクエスト情報: {request_by_flask}")
  logger.error(e)
  return render_template('errors/404.html'), 404

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
    self.csrf = CSRFProtect(self.__flask)
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

    # templateの定義を取得
    import template_filters
    filters = inspect.getmembers(template_filters, inspect.ismethod if _py2 else inspect.isfunction)
    for filter in filters:
      _, function = filter
      self.__flask.add_template_filter(function)
    
    # エラー関連処理
    self._register_error()

  def test_client(self):
    """テストクライアントの返却

    Returns:
        client: テストクライアント
    """
    self.__flask.config['TESTING'] = True
    self.__flask.config['WTF_CSRF_ENABLED'] = False

    return self.__flask.test_client()

  def before_request(self, function):
    """リクエスト実行前のロジックを設定する

    Args:
        function (f): 実行するメソッド
    """
    self.__flask.before_request(function)

  def after_request(self, function):
    """リクエスト実行後のロジックを設定する

    Args:
        function (f): 実行するメソッド
    """
    self.__flask.after_request(function)

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
  
  def _register_error(self):
    """エラーハンドラの登録処理
    """
    # 404エラーの場合のエラーハンドラの登録
    self.__flask.register_error_handler(404, _page_not_found)
    # 内部サーバエラーの場合のエラーハンドラの登録
    self.__flask.register_error_handler(500, _internal_server_error)

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

  def get_db_connector(self):
    return self._connector


_beaker_db = BeakerDB(get_config(), logger)
def start_transaction(read_only = True):
  """トランザクション開始処理

  Args:
      read_only (bool, optional): 読み込み専用か？ 読み込み専用の場合はTrueとなりコミットを行わない. Defaults to True.

  Returns:
      Transaction: トランザクションを返却する
  """
  logger.debug(f'read_only: {read_only}')
  return _beaker_db.start_transaction(read_only=read_only)

def create_query_builder(tx=None):
  if tx is None:
    return QueryBuilder(logger, db_conecter=_beaker_db.get_db_connector())
  return QueryBuilder(logger, tx=tx)

request = request_by_flask

def create_csv(headers):
  """CSV出力のCreatorを返却する

  Args:
      headers (dict): keyとヘッダ名の辞書を返却

  Returns:
      CsvCreator: CsvCreatorの返却
  """
  logger.debug(f'headers: {headers}')
  return CsvCreator(logger, headers)

def make_csv_response(csv_data, file_name, chara_set='shift_jis'):
  """CSVのレスポンスを返却する

  Args:
      csv_data (stream): CSVの値
      file_name(str): CSVファイル名(拡張子は不要)
  Returns:
      response: csvのレスポンスを返却する
  """
  logger.debug(f'csv_data: {csv_data}')
  logger.debug(f'file_name: {file_name}')
  logger.debug(f'chara_set: {chara_set}')
  response = make_response()
  response.data = csv_data
  response.headers['Content-Type'] = f'text/csv; charset={chara_set}'
  response.headers['Content-Disposition'] = f'attachment; filename={file_name}.csv'
  return response
