load("xpath.star", "xpath")
load("pixlib/_rpc.star", "_rpc")

def html.unescape(text):
  if not text:
    return text
  return _rpc.function("html.unescape", [text])

def html.to_xml(text):
  if not text:
    return text
  return _rpc.function("html.to_xml", [text])

def html.xpath(text):
  return xpath.loads(html.to_xml(text))
