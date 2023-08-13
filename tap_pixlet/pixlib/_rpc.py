import sys
import json

def html__unescape(s):
    import html
    return html.unescape(s)

def html__to_xml(s):
    from lxml import html, etree
    return etree.tostring(html.fromstring(s)).decode("utf-8")

def input__read():
    import os
    return os.getenv("APP_INPUT")

functions = {
    "html.unescape": html__unescape,
    "html.to_xml": html__to_xml,
    "input.read": input__read
}

input = json.loads(sys.argv[1])
function = input["function"]
args = input["args"]

if not function in functions:
    raise Exception(f"Function '{function}' not found")

# TODO: Check if function length matches number of args
result = functions[function](*args)

output = {"result": result}
print(json.dumps(output))
