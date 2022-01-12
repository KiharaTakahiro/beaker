import yaml

def load_yaml(file_name):
  """ yamlファイルの読込処理
      ※読込エラーがある場合を考慮しないためハンドルする側で考慮すること
  """
  with open(file_name) as file:
    return yaml.safe_load(file.read())