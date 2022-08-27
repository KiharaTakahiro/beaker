from io import StringIO
import csv

class CsvCreator():
  """ CSVの作成処理を行うためのクラス
  """

  def __init__(self, headers):
    """ CSV作成処理の初期化

    Args:
        logger (logging): loggingのlogger
        headers (dict): keyと表示ヘッダーの値の辞書
    """
    self.__headers = headers

  def __create_data(self):
    """ CSVのデータ作成
    """
    self.__data = StringIO()
    self.__writer = csv.writer(self.__data, quotechar='"', quoting=csv.QUOTE_ALL, lineterminator="\n")

  def __write_header(self):
    """ ヘッダー書き込み処理
    """
    self.__writer.writerow(self.__headers.values())

  def write_row(self, data_row):
    """ CSVの行書き込み処理

    Args:
        data_row (dect): headerのkeyにマッピングするvalue
    """
    csv_row = []
    for key in self.__headers.keys():
      if key in data_row:
        csv_row.append(data_row[key])
      else:
        # 存在しないkeyの場合は空文字に変換する
        csv_row.append("")
    self.__writer.writerow(csv_row)

  def getvalue(self, encode='utf_8_sig'):
    """ CSVデータの取得処理

    Returns:
        stream: CSVの値
    """
    return self.__data.getvalue().encode(encode)

  def __enter__(self):
    self.__create_data()
    self.__write_header()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.__data.close()
    if exc_type is not None:
      raise Exception(f"CSV作成処理でエラーが発生しました。")

