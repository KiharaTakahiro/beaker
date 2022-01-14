from common.beaker import render_template, request

def welcome():
  welcome_text = "WLECOME BEAKER"
  return render_template('welcome.html', welcome_text = welcome_text)

def welcome_post():
  return render_template('welcome-post.html', post_text = request.form['welcome-text'])
