load("http.star", "http")

def file._url(config, path):
    ASSET_URL = config.get("$asset_url")
    if not ASSET_URL:
        fail("Missing '$asset_url' config. Ensure tap-pixlet 'path' config is set to a directory.")

    return ASSET_URL + path

def file.read(config, path, json=False):
    url = file._url(config, path)
    response = http.get(url)
    if response.status_code != 200:
        fail("File not found:", path)

    if json:
        return response.json()
    else:
        return response.body()

def file.json(config, path):
    return file.read(config, path, json=True)

def file.exec(config, path, json=None, input=None):
    url = file._url(config, path)

    options = {}
    if json:
        options["json_body"] = json
    elif input:
        options["body"] = input

    response = http.post(url, **options)
    if response.status_code != 200:
        fail("Failed to execute '{}': " % path, response.json()["error"])

    if response.headers['Content-Type'] == 'application/json':
        return response.json()
    else:
        return response.body()
