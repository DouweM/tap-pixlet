import sys
import json

def html__unescape(s):
    import html
    return html.unescape(s)

functions = {
    "html.unescape": html__unescape
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
