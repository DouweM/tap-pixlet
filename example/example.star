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

    return render.Root(
        child=render.Box(
          child=render.Image(src=image_data(ASSET_URL + 'example.png'), width=WIDTH)
        )
    )
