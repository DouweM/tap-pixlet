load("pixlib/_rpc.star", "_rpc")

def file.read(path, json=False):
    return _rpc.read(path, json=json)

def file.json(path):
    return file.read(path, json=True)

def file.exec(path, json=None, input=None):
    return _rpc.execute(path, json=json, input=input)
