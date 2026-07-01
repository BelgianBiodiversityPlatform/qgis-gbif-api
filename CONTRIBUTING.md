# Contributing / local development

## How a QGIS plugin runs (important)

This plugin imports `qgis` and `PyQt`, which **only exist inside QGIS's own
bundled Python interpreter**. You cannot `pip install qgis` into a normal
virtual environment. There are therefore two separate "Pythons" in play:

- **Runtime Python = QGIS's bundled interpreter.** You do not choose it; QGIS
  ships it. The plugin runs here, inside QGIS.
- **Tooling Python = a small local environment** (managed by `uv`, below) used
  only for development *tooling* such as `qgis-plugin-ci`. It never imports
  `qgis`.

So the local environment described here is for building/releasing and tooling,
**not** for running the plugin. You run the plugin by loading it into QGIS (see
"Testing in QGIS").

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (`brew install uv` or
  `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- git
- QGIS (3.16+ or 4.x) for actually running the plugin

## Set up the tooling environment

```bash
uv sync
```

This reads [`pyproject.toml`](pyproject.toml) + [`.python-version`](.python-version),
creates a `.venv/` with Python 3.12, and installs `qgis-plugin-ci`. Run tools
through `uv run` so the right environment is always used:

```bash
uv run qgis-plugin-ci --help
```

> If you have a pyenv/virtualenv active in your shell, uv prints a harmless
> `VIRTUAL_ENV ... does not match` warning and correctly uses `.venv` anyway.
> You can ignore it, or `pyenv deactivate` first.

> Never add `qgis` to `pyproject.toml` - it is not pip-installable and is
> provided by QGIS at runtime.

## Build the plugin zip locally

To produce the exact zip that a release would publish, without publishing
anything:

```bash
uv run qgis-plugin-ci package 0.4.0
```

This writes `GBIFOccurrences.<version>.zip` containing the `GBIFOccurrences/`
folder. The version argument is just a label for the file - use whatever you
like for a test build (e.g. `0.4.0-test`).

**`package` refuses to run if you have uncommitted changes** (it normally builds
from committed git content). While iterating on a branch, add
`--allow-uncommitted-changes` (short `-c`) to package your current working tree:

```bash
uv run qgis-plugin-ci package 0.4.0-test --allow-uncommitted-changes
```

The `Changelog file doesn't exist: CHANGELOG.md` warning is expected - this
plugin keeps its changelog inside `GBIFOccurrences/metadata.txt`, not a separate
file.

## Testing in QGIS

**Quick check of a built zip:** in QGIS, **Plugins -> Manage and Install
Plugins -> Install from ZIP**, point it at the zip from the previous step, then
enable the plugin.

**Live development** (no rebuild on every change): symlink the plugin folder
into your QGIS profile's plugin directory, then use the *Plugin Reloader*
plugin to reload after edits.

```bash
# macOS
ln -s "$(pwd)/GBIFOccurrences" \
  ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/GBIFOccurrences

# Linux
ln -s "$(pwd)/GBIFOccurrences" \
  ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/GBIFOccurrences
```

## Releasing

Cutting an actual release (GitHub release + publishing to plugins.qgis.org) is
automated via a git tag and GitHub Actions. See [RELEASING.md](RELEASING.md).
