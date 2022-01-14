from common.beaker import get_session, set_session, render_template, request, logger

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
