"""このパッケージにて定義されたメソッドはカスタムフィルタとして抽出されます。
"""
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

def concat_list(target_list, delimiter=',', empty_text='', exception_text=''):
  """リスト形式の文字列にデリミタをつけて結合する
     例) ["a", "b", "c"] → "a,b,c"
  Args:
      target_list (list): 結合対象文字列
      delimiter (str, optional): 区切り文字. Defaults to ','.
      empty_text (str, optional): リストが空の場合の返却文字列. Defaults to ''.
      exception_text (str, optional): 想定外文字列の場合の返却. Defaults to ''.
  Returns:
      str: 結合した文字列
  """
  try:
    logger.debug(f'リスト形式の文字列結合処理のtarget_list: {target_list}')

    # 与えられた対象がリストでない場合は後続処理は行わない(想定外の結合が行われるのを防止する)
    if type(target_list) is not list:
      # HACK: 全体的に表示に関わる部分でエラーにしないようにしたほうが良いと考えてエラー専用の文字列返却を行っている
      #       運用の中でエラーの発見を起こすリスクも考えた上で再度検討しても良いと考えている
      logger.warning(f'リスト結合処理で失敗しています。 与えられた引数はリストではありません。 {target_list}')
      return exception_text

    # リストが空の場合は特定の別途返却文字列を返す
    if len(target_list) == 0:
      return empty_text

    # リストを結合した文字列を返却
    return delimiter.join(target_list)

  except Exception:
    # HACK: 全体的に表示に関わる部分でエラーにしないようにしたほうが良いと考えてエラー専用の文字列返却を行っている
    #       運用の中でエラーの発見を起こすリスクも考えた上で再度検討しても良いと考えている
    logger.warning(f'リスト結合処理で失敗しています。 list: {target_list}, delimiter: {delimiter}')
    return exception_text