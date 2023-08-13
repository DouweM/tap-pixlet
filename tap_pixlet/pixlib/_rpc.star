load("http.star", "http")

_rpc.URL = "<<PIXLIB_RPC_URL>>" # Inserted by tap-pixlet

def _rpc._file_url(path):
    if not _rpc.URL:
        fail("Missing Pixlib RPC URL. Ensure tap-pixlet 'path' config is set to a directory.")

    return _rpc.URL + path

def _rpc.read(path):
    url = _rpc._file_url(path)

    response = http.get(url)
    if response.status_code != 200:
        fail("File not found:", path)

    if path.endswith('.json'):
        return response.json()
    else:
        return response.body()

def _rpc.execute(path, json=None, input=None):
    url = _rpc._file_url(path)

    options = {}
    if json:
        options["json_body"] = json
    elif input:
        options["body"] = input

    response = http.post(url, **options)
    if response.status_code != 200:
        fail("Failed to execute '{}': {}".format(path, response.json()["error"]))

    if 'Content-Type' in response.headers and response.headers['Content-Type'] == 'application/json':
        return response.json()
    else:
        return response.body()

def _rpc.function(function, args = []):
    return _rpc.execute("pixlib/_rpc.py", {"function": function, "args": args})["result"]

