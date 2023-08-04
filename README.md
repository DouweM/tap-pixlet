# `tap-pixlet`

`tap-pixlet` is the unofficial [Tidbyt](https://tidbyt.com) app runner that powers [Pixbyt](https://pixbyt.dev), the self-hosted Tidbyt app server for advanced apps that aren't supported by the official [community app](https://tidbyt.dev/docs/publish/community-apps) server that you can access through Tidbyt's mobile app.

It extends [Pixlet](https://github.com/tidbyt/pixlet) (the official Tidbyt app development framework) with an unofficial standard library named [Pixlib](./tap_pixlet/pixlib), similar to how [Starlib](https://github.com/qri-io/starlib) is the unofficial standard library for [Starlark](https://github.com/google/starlark-go) (the Python-like language Tidbyt apps are written in).

`tap-pixlet` was built using the [Meltano SDK](https://sdk.meltano.com), and is intended to be run using Pixbyt, which combines it with
[`target-tidbyt`](https://github.com/DouweM/target-tidbyt) and [`target-webp`](https://github.com/DouweM/target-tidbyt) using [Meltano](https://github.com/meltano/meltano).

## Usage

See [Pixbyt](https://pixbyt.dev).

## Pixlib

See [Pixlib](./tap_pixlet/pixlib/).
