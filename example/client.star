load("pixlib/file.star", "file")

def client.get_image(config):
    return file.read(config, "meltano.png")

def client.get_response(config, name):
    return file.exec(config, "hello.py", {"name": name})["response"]
