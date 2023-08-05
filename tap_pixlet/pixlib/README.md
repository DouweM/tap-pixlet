# Pixlib

Pixlib is the unofficial standard library for [Pixlet](https://github.com/tidbyt/pixlet) (the official Tidbyt app development framework), similar to how [Starlib](https://github.com/qri-io/starlib) is the unofficial standard library for [Starlark](https://github.com/google/starlark-go) (the Python-like language Tidbyt apps are written in).

Pixlib is included with [`tap-pixlet`](https://github.com/DouweM/tap-pixlet), the unofficial [Tidbyt](https://tidbyt.com) app runner that powers [Pixbyt](https://pixbyt.dev), the self-hosted Tidbyt app server for advanced apps that aren't supported by the official [community app](https://tidbyt.dev/docs/publish/community-apps) server that you can access through Tidbyt's mobile app.

## Usage

See [Pixbyt](https://pixbyt.dev).

## Modules

### `pixlib/const`

```python
load("pixlib/const.star", "const")
```

- `const.WIDTH = 64`: Width of the Tidbyt display
- `const.HEIGHT = 32` Height of the Tidbyt display
- `const.FPS = 20`: Framerate (in frames/second) of the Tidbyt display

### `pixlib/file`

```python
load("pixlib/file.star", "file")
```

- `file.read(path)`: Read local file. Returns contents as a (byte)string or deserialized JSON object.
- `file.exec(path, json?, input?)`: Execute local Python script, with optional JSON or plaintext input (provided to the script as a command line argument). Returns script's output as a string or deserialized JSON object.

### `pixlib/font`

```python
load("pixlib/font.star", "font")
```

- `font.height(font)`: Get height of named [font](https://tidbyt.dev/docs/build/fonts-in-pixlet) in pixels.

### `pixlib/html`

```python
load("pixlib/html.star", "html")
```

- `html.unescape(text)`: Convert HTML-escaped character references (e.g. `&gt;`, `&#62;`, `&#x3e;`) to the corresponding Unicode characters. See [Python `html.unescape`](https://docs.python.org/3/library/html.html#html.unescape).

- `html.to_xml(text)`: Convert HTML text to XML.

- `html.xpath(text)`: Returns an [XPath object](https://tidbyt.dev/docs/reference/modules#pixlet-module-xpath) for HTML text.

## Functions

### `load`

The [`load` statement](https://tidbyt.dev/docs/reference/modules) has been overloaded to support the above Pixlib modules, as well as local Starlark files.

```python
load("<path>", "<module>")

# Examples:

# Standard (Pixlet, Starlib)
load("render.star", "render")
# Pixlib
load("pixlib/const.star", "const")
# Local
load("./client.star", "client")
```

#### Local Starlark modules

Your Starlark applet can load modules containing constants and functions from other local Starlark files.

##### Define

```python
# `./<module>.star`

<module>.<CONSTANT_NAME> = <value>

def <module>.<function>(<args...>):
  <body>

# Example:

# `./client.star`
load("http.star", "http")

client.URL = "https://example.com/api/%s.json"

def client.load(path):
  return http.get(client.URL % path)
```

##### Reference

```python
load("./<path>", "<module>")

def main():
  result = <module>.<function>(<args...>)

# Example:

# `my-app.star`
load("./client.star", "client")

def main():
  items = client.load("items")
  # ...
```
