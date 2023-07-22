load("pixlib/_rpc.star", "_rpc")

def html.unescape(text):
  if not text:
    return text
  return _rpc.function("html.unescape", [text])
