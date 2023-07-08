load("pixlib/_rpc.star", "_rpc")

def file.read(path):
    return _rpc.read(path)

def file.exec(path, json=None, input=None):
    return _rpc.execute(path, json=json, input=input)
