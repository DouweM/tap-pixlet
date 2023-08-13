load("pixlib/_rpc.star", "_rpc")
load("encoding/json.star", "json")

def input.read():
  return _rpc.function("input.read")

def input.json():
  data = input.read()
  if not data:
    return {}
  return json.decode(data)
