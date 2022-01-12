import psycopg2
from psycopg2.extras import DictCursor

class DbConnecter():
  """DBの接続情報をもつクラス

  """
  def __init__(self, dbname: str, host: str, user: str, password: str):
    self.__setting(dbname, host, user, password)
  
  def __setting(self, dbname: str, host: str, user: str, password:str):
    self.__dbname = dbname
    self.__host = host
    self.__user = user
    self.__password = password
  
  def __str__(self):
    return f"DB名: {self.__dbname}, ホスト: {self.__host}, ユーザ: {self.__user}, パスワード: {self.__password}"

  def get_connect(self):
    return psycopg2.connect(f"dbname={self.__dbname} host={self.__host} user={self.__user} password={self.__password}")

class Transaction():
  """ トランザクションを処理を実行するためのクラス
      connector: DBConnecterクラスを使用したDBへの接続情報
      logger: loggingのlogger
      read_only:  読み込み用のトランザクション: true(初期値) 登録用のトランザクション: false
      schema: schemaを指定することでトランザクションのスキーマを変更

      使用例) 
      ・DBからのデータ取得の場合
      with Transaction(connector, logger, true) as tx
        results = tx.find_all(query)

      ・DBへのデータ登録の場合
      with Transaction(connector, logger, false) as tx
        tx.save(query)

      ・DBからデータを削除の場合
      with Transaction(connector, logger, false) as tx
        tx.delete(query)
  """
  def __init__(self, connector: DbConnecter, logger, read_only=True, schema=None):
    self.__connector = connector
    self.__read_only = read_only
    self.__schema = schema
    self.__logger = logger

  def open(self):
    """ トランザクションを開始する
    """
    self.__logger.debug(f'DB接続情報 {self.__connector}')
    self.__connect = self.__connector.get_connect()

  def close(self, success_flg=True):
    """ トランザクションを終了する
        読み込みモードの場合は処理が成功したか否かでトランザクションをコミットするかロールバックするかを分ける
        success_flg: 処理成功の場合: true(初期値) 処理失敗の場合はfalse 
    """
    if not self.__read_only:
      if success_flg: 
        self.__connect.commit()
      else:
        self.__connect.rollback()
    self.__connect.close()

  def find_all(self, query, vars=None):
    """ 全件取得
    """
    self.__logger.debug(f'sql: {query}')
    self.__logger.debug(f'vars: {vars}')
    with self.__connect.cursor(cursor_factory = DictCursor) as cur:
      cur.execute(query, vars)
      result = cur.fetchall()
      self.__logger.debug(f'result: {result}')
      return result
  
  def find_one(self, query, vars=None):
    """ 1件取得
    """
    self.__logger.debug(f'sql: {query}')
    self.__logger.debug(f'vars: {vars}')
    with self.__connect.cursor(cursor_factory = DictCursor) as cur:
      cur.execute(query, vars)
      result = cur.fetchone()
      self.__logger.debug(f'result: {result}')
      return result

  def save(self, query, vars = None):
    """ 保存処理
    """
    self.__logger.debug(f'sql: {query}')
    self.__logger.debug(f'vars: {vars}')
    with self.__connect.cursor() as cur:
      cur.execute(query, vars)

  def delete(self, query, vars = None):
    """ 削除処理
    """
    self.__logger.debug(f'sql: {query}')
    self.__logger.debug(f'vars: {vars}')
    with self.__connect.cursor() as cur:
      cur.execute(query, vars)

  def change_schema(self, schema_name):
    """ スキーマの変更
    """
    self.__logger.info(f'schema_name: {schema_name}')
    with self.__connect.cursor() as cur:
      cur.execute(f'SET search_path TO {schema_name},public;')

  def execute_ddl(self, query):
    """DDL実行用の処理
       NOTE: DDLの実行がトランザクションクラスで行えるのは微妙だと思うものの
       接続情報等を使いまわして使用できる方が利便性があるなと思い、ここで実行できるようにする

    Args:
        query (str): 実行するDDL
    """
    with self.__connect.cursor() as cur:
      cur.execute(query, vars)

  def __enter__(self):
    self.open()
    if self.__schema is not None:
      self.change_schema(self.__schema)
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    if exc_type is not None:
      self.__logger.error(f'エラーの種類: {exc_type}')
      self.__logger.error(f'エラーの値: {exc_value}')
      self.__logger.error(traceback)
    self.close(exc_type is None)
