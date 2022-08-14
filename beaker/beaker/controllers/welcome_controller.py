from common.beaker import get_session, set_session, render_template, request, logger, create_csv, make_csv_response, create_query_builder, start_transaction

def welcome():
  welcome_text = "WLECOME BEAKER"
  logger.debug('debugログの出力')
  logger.info('infoログの出力')
  logger.warning('warningログの出力')
  logger.error('errorログの出力')
  set_session('key', 'value')
  return render_template('welcome.html', welcome_text = welcome_text)

def welcome_post():
  session_value = get_session('key')
  logger.debug(f'session_value: {session_value}')
  return render_template('welcome-post.html', post_text = request.form['welcome-text'])

def welcome_get_csv():
  # ヘッダ行
  headers = {
    'test1': 'テスト1', 
    'test2': 'テスト2'
    }

  with create_csv(headers) as cc:
    # 1行目の書き込み
    row1 = {
      'test1': 'テスト1-1',
      'test2': 'テスト2-1'
    }
    cc.write_row(row1)

    # 2行目の書き込み
    row2 = {
      'test1': 'テスト1-2',
      'test2': 'テスト2-2'
    }
    cc.write_row(row2)
    csv_data = cc.getvalue()
  # test.csvとしてダウンロードさせる
  return make_csv_response(csv_data, 'test')

def welcome_db():
  # 以下は使用サンプルのため、適宜書き換えてご確認ください
  # with start_transaction() as tx:
  #   query_builder = create_query_builder(tx)
  #   client = query_builder.table('{テーブル名}').where('{フィールド名}', '=', 2).or_where('{フィールド名2}', '=', 3).select()
  # with start_transaction(False) as tx:
  #   query_builder = create_query_builder(tx)
  #   query_builder.table('{テーブル名}').insert({'{フィールド名}': 6, '{フィールド名2}': 'test'})
  # return render_template('welcome.html', welcome_text = 'DBの取得を行いました')
  # with start_transaction(False) as tx:
  #   query_builder = create_query_builder(tx)
  #   query_builder.table('{テーブル名}').where('{フィールド名}', '=', 6).update({'{フィールド名2}': 'test2'})
  # with start_transaction(False) as tx:
  #   query_builder = create_query_builder(tx)
  #   query_builder.table('{テーブル名}').where('{フィールド名}', '=', 6).delete()
  return render_template('welcome.html', welcome_text = 'DBに関する確認')

def welcome_error_test():
  raise Exception('エラー発生を確認するテストのためのメソッド!!')