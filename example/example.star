load("render.star", "render")
load("http.star", "http")
load("cache.star", "cache")

WIDTH = 64
HEIGHT = 32

def image_data(url):
    cached = cache.get(url)
    if cached:
        return cached

    response = http.get(url)

    if response.status_code != 200:
        fail("Image not found", url)

    data = response.body()
    cache.set(url, data)

    return data

def main(config):
    ASSET_URL = config.get("$asset_url")
    NAME = config.get("name")

    image = image_data(ASSET_URL + 'meltano.png')

    response = http.post(ASSET_URL + 'hello.py', json_body={"name": NAME})
    if response.status_code != 200:
        fail("Script failed", response.json()["error"])
    text = response.json()["response"]

    return render.Root(
        child=render.Column(
            expanded=True,
            main_align="space_around",
            cross_align="center",
            children=[
                render.Image(src=image, width=WIDTH),
                render.Text(text)
            ]
        )
    )
