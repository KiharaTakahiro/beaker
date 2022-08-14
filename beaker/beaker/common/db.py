import psycopg2
from psycopg2.extras import DictCursor

class DbConnecter(object):
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

class Transaction(object):
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
      self.__logger.error(f'エラーの種類: {exc_type}\nエラーの値: {exc_value}\n{traceback}')
    self.close(exc_type is None)

from abc import ABC, abstractclassmethod
from enum import Enum

class FiledType(Enum):
  AND = "AND"
  OR = "OR"

class QueryConditon(ABC):
  """ クエリの条件式"""

  @abstractclassmethod
  def get_condition(self):
    pass

class ConditionPart(QueryConditon):

  def __init__(self):
    self._filed_type = None

  def where(self, filed_name, eval, value):
    self._fild_name = filed_name
    self._eval = eval
    self._value = value
    self._filed_type= FiledType.AND

  def or_where(self, filed_name, eval, value):
    self._fild_name = filed_name
    self._eval = eval
    self._value = value
    self._filed_type= FiledType.OR

  def get_condition(self):
    return f"{self._fild_name} {self._eval} {_define_value_type(self._value)}", self._filed_type, [self._value]

class ConditionGroup(QueryConditon):
  def __init__(self, condition_type, root_condition=False):
    self._conditions = []
    self._values = []
    self._condition_type = condition_type
    self._root_condition = root_condition

  def add(self, condition):
    self._conditions.append(condition)
  
  def get_condition(self):
    
    if len(self._conditions) == 0:
      raise Exception("conditionが存在しません")
    
    ret_condition = ""
    for index, condition in enumerate(self._conditions):
      conditon_str, conditon_type, condition_value = condition.get_condition()
      if index != 0:
        ret_condition += f' {conditon_type.value} '
      ret_condition += f' {conditon_str} '
      self._values.extend(condition_value)
    if not self._root_condition and len(self._conditions) > 1:
      ret_condition = f"({ret_condition}) "
    return ret_condition, self._condition_type, self._values
  
  def exists(self):
    return len(self._conditions) != 0

import re

class QueryBuilder(object):
  """ QueryBuilder"""

  def __init__(self, logger, db_conecter=None, tx=None):
    self._table_name = None
    self._conditions = ConditionGroup(FiledType.AND, True)
    self._logger = logger
    if tx is None and db_conecter is None:
      raise Exception("トランザクションかDBのコネクタは必須です")
    elif tx is not None and db_conecter is not None:
      raise Exception("トランザクションかDBコネクタはどちらかのみを設定してください")
    self._db_conecter = db_conecter
    self._tx = tx
  
  def table(self, table_name, schema=None):
    """ テーブル名の指定を行う

    Args:
        table_name (str): テーブル名
    """
    self._table_name = table_name
    if self._tx is None and schema is not None:
      raise Exception("スキーマはトランザクションごとに指定してください")
    self._schema = schema
    return self

  def where(self, filed_name, eval, value):
    condition_part = ConditionPart()
    condition_part.where(filed_name, eval, value)
    condition_group = ConditionGroup(FiledType.AND)
    condition_group.add(condition_part)
    self._conditions.add(condition_group)
    return self

  def or_where(self, filed_name, eval, value):
    condition_part = ConditionPart()
    condition_part.or_where(filed_name, eval, value)
    condition_group = ConditionGroup(FiledType.OR)
    condition_group.add(condition_part)
    self._conditions.add(condition_group)
    return self

  def select(self, *args):
    query, query_values = self._query_build(self.__create_select_clause(*args))
    
    if self._tx is not None:
      return self.__find_all(query, query_values, self._tx)
    else:
      with Transaction(self._db_conecter, self._logger, True, self._schma) as tx:
        return self.__find_all(query, query_values, tx)

  def select_one(self, *args):
    query, query_values = self._query_build(self.__create_select_clause(*args))
    
    if self._tx is not None:
      return self.__find_one(query, query_values, self._tx)
    else:
      with Transaction(self._db_conecter, self._logger, True, self._schma) as tx:
        return self.__find_one(query, query_values, tx)

  def __create_select_clause(self, *args):
    self._logger.debug(args)
    select_filed = "*"
    if len(args) != 0:
      select_filed = ', '.join(args)
    return f"SELECT {select_filed} FROM {self._table_name}"

  def __find_all(self, query, query_values, tx):
    query = self._crean_query(query)
    if len(query_values) != 0:
      return tx.find_all(query, tuple(query_values))
    else:
      return tx.find_all(query)

  def __find_one(self, query, query_values, tx):
    query = self._crean_query(query)
    if len(query_values) != 0:
      return tx.find_one(query, tuple(query_values))
    else:
      return tx.find_one(query)

  def update(self, update_dict):
    if update_dict is None or not any(update_dict):
      raise Exception("アップデートのキーが存在しません")
    before_query = f"UPDATE {self._table_name} SET "
    update_values = []
    for index, key in enumerate(update_dict.keys()):
      if index != 0:
        before_query += ", "
      before_query += f"{key} = {_define_value_type(update_dict[key])}"
      update_values.append(update_dict[key])
    query, query_values = self._query_build(before_query)
    update_values.extend(query_values)

    query = self._crean_query(query)
    if self._tx is not None:
      self._tx.save(query, tuple(update_values))
    else:
      with Transaction(self._db_conecter, self._logger, True, self._schma) as tx:
        tx.save(query, tuple(update_values))

  def delete(self):
    query, query_values = self._query_build("DELETE FROM {self._table_name} ")
    query = self._crean_query(query)
    if self._tx is not None:
      self._tx.save(query, tuple(query_values))
    else:
      with Transaction(self._db_conecter, self._logger, True, self._schma) as tx:
        tx.save(query, tuple(query_values))

  def insert(self, insert_dict):
    if self._table_name is None:
      raise Exception("テーブルが指定されていません")
    if insert_dict is None or not any(insert_dict):
      raise Exception("アップデートのキーが存在しません")
    insert_values = []
    key_query = ""
    value_query = ""
    for index, key in enumerate(insert_dict.keys()):
      if index != 0:
        key_query += ", "
        value_query += ", "
      key_query += key
      value_query += _define_value_type(insert_dict[key])
      insert_values.append(insert_dict[key])
    query = f"INSERT INTO {self._table_name} ({key_query}) VALUES ({value_query})"
    query = self._crean_query(query)
    if self._tx is not None:
      self._tx.save(query, tuple(insert_values))
    else:
      with Transaction(self._db_conecter, self._logger, True, self._schma) as tx:
        tx.save(query, tuple(insert_values))

  def _query_build(self, before_query="SELECT * FROM"):
    if self._table_name is None:
      raise Exception("テーブルが指定されていません")

    query = f"{before_query}"
    query_values = []
    if self._conditions.exists():
      query_str, _, query_values = self._conditions.get_condition()
      query += f" WHERE {query_str}"
    return query, query_values
  
  def _crean_query(self, query):
    query = re.sub('[ 　]+', ' ', query)
    query = re.sub(' $','', query)
    query += ';'
    return query

def _define_value_type(value):
  """ 値のタイプをもとにDBの値を返却する

  Args:
      value (any): 値を返却する
  """
  if type(value) is str or type(value) is int:
    return "%s"
  elif type(value) is dict or type(value) is list:
    return "%s::json"
  else:
    return "%s"
