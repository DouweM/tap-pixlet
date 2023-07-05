load("pixlib/_rpc.star", "_rpc")

def html.unescape(text):
  return _rpc.function("html.unescape", [text])
