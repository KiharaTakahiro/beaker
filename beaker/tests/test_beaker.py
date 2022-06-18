from beaker import __version__
from beaker.app_run import app

def test_version():
  assert __version__ == '0.1.0'

def test_route():
  client = app.test_client()
  response = client.get('/')
  assert response.status_code == 200


