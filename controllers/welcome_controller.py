from common.beaker import render_template, request, logger

def welcome():
  welcome_text = "WLECOME BEAKER"
  logger.debug('debugログの出力')
  logger.info('infoログの出力')
  logger.warning('warningログの出力')
  logger.error('errorログの出力')
  return render_template('welcome.html', welcome_text = welcome_text)

def welcome_post():
  return render_template('welcome-post.html', post_text = request.form['welcome-text'])
