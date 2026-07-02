# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A QGIS plugin ("GBIF Occurrences") that downloads GBIF occurrence records from
the [GBIF occurrence search API](http://api.gbif.org/v1/) and imports them as a
point layer directly inside QGIS. Supports QGIS 3.16+ and 4.x.

## Two-Python model (read this first)

There are two distinct Python interpreters in play, and confusing them is the
main source of mistakes:

- **Runtime Python = QGIS's own bundled interpreter.** The plugin (everything
  under `GBIFOccurrences/`) runs here. It imports `qgis` and `PyQt`, which are
  **only available inside QGIS** - you cannot `pip install qgis`. Do not add
  `qgis` or `PyQt` to `pyproject.toml`.
- **Tooling Python = the local `uv`-managed `.venv/`.** Used only for
  development *tooling* (`qgis-plugin-ci` for packaging/releasing). It never
  imports `qgis`.

So `pyproject.toml` describes the tooling env, not the plugin's dependencies.
The plugin's runtime dependency (`requests`) is provided by QGIS, not declared here.

## Common commands

Set up / run tooling (through `uv run` so the right env is used):

```bash
uv sync                                    # create .venv with qgis-plugin-ci
uv run qgis-plugin-ci package 0.4.0        # build GBIFOccurrences.<version>.zip from committed content
uv run qgis-plugin-ci package 0.4.0-test --allow-uncommitted-changes   # build from working tree while iterating
```

`package` refuses to run with uncommitted changes unless you pass
`--allow-uncommitted-changes` (`-c`). The `CHANGELOG.md doesn't exist` warning
is expected - the changelog lives in `GBIFOccurrences/metadata.txt`.

Live development in QGIS: symlink `GBIFOccurrences/` into the QGIS profile's
plugin dir and use the *Plugin Reloader* plugin (exact paths in
[CONTRIBUTING.md](CONTRIBUTING.md)).

**Tests** (`test/`) are legacy unittest suites that mock the GBIF API with
`httmock` and must run under QGIS's Python with the `QtTest` module. The README
invokes `make test`, but there is currently **no Makefile at the repo root**,
and tests are known to be hard/impossible to run on macOS (Kyngchaos QGIS
bundles PyQt without `QtTest`). Do not assume `make test` works; verify the
harness before claiming tests pass.

## Releasing

Automated via git tag - see [RELEASING.md](RELEASING.md). Bump `version=` and
the `changelog=` block in `GBIFOccurrences/metadata.txt`, then push a **bare**
version tag (no `v` prefix): `git tag 0.4.1 && git push origin 0.4.1`. The tag
string is written verbatim into `metadata.txt` by qgis-plugin-ci, so it must
match `version=`. The tag push triggers `.github/workflows/release.yaml`, which
builds the zip, creates the GitHub release, and publishes to plugins.qgis.org.

## Architecture

The shipped plugin is the `GBIFOccurrences/` directory (the one containing
`metadata.txt`). **Its folder name must stay `GBIFOccurrences`** - qgis-plugin-ci
uses it for both the zip name and the installed folder name, so renaming breaks
existing users' upgrades. Everything at the repo root (README, tests,
screenshots, tooling config) is dev-only and is not shipped in the zip.

Module responsibilities and flow:

- `__init__.py` - `classFactory(iface)` is the QGIS entry point; it instantiates
  the plugin class.
- `qgis_occurrences.py` - `GBIFOccurrences`, the plugin lifecycle class. Wires
  the menu/toolbar action (`initGui`/`unload`), owns the dialog, and in `run()`
  adds an OSM basemap when the project has no layers (so the user has something
  to draw a bbox on).
- `qgis_occurrences_dialog.py` - `GBIFOccurrencesDialog`, the main controller.
  Loaded from `qgis_occurrences_dialog_base.ui` via `uic.loadUiType`. Translates
  UI widgets into a GBIF filter dict (`_ui_to_filters`), orchestrates count ->
  fetch -> add-to-layer, and drives progress/stop UI. `load_occurrences()` is
  the central action.
- `gbif_webservices.py` - all HTTP to GBIF. `count_occurrences()` (pre-flight
  count, warns above `WARNING_THRESHOLD`, hard-caps at `MAX_TOTAL_RECORDS_GBIF`
  = 200k, a GBIF API limit) and `get_occurrences_in_batches()` (a **generator**
  paging `RECORDS_PER_PAGE`=300 at a time, keeping the UI responsive). Raises
  `ConnectionIssue` / `GBIFApiError`, which the dialog catches.
- `helpers.py` - builds the output. `create_and_add_layer()` makes an in-memory
  EPSG:4326 point layer; `add_gbif_occ_to_layer()` adds one feature per record,
  **creating layer attributes dynamically** from whatever JSON keys each record
  has (complex values are JSON-serialized into the field). Geometry comes from
  `decimalLongitude`/`decimalLatitude`.
- `rectangle_tool.py` - `RectangleDrawTool`, a `QgsMapTool` for drawing a bbox
  on the canvas. Reprojects the drawn extent from the project CRS to EPSG:4326
  (GBIF's CRS) and emits a signal when done.

Search modes are mutually exclusive in `_ui_to_filters`: bbox (`geometry`) vs
country/GADM boundaries. Country selection reads a CSV from
`QgsApplication.metadataPath()` (`country_code_ISO_3166.csv`), not a bundled
file.

## QGIS 3 vs 4 compatibility

The code targets both major versions, guarded on `Qgis.QGIS_VERSION_INT`. When
touching Qt/QGIS APIs, keep both paths working. Known guarded spots:

- `QIODeviceBase.OpenModeFlag.ReadOnly` (QGIS 4) vs `QIODevice.ReadOnly` (QGIS 3)
  in `qgis_occurrences_dialog.get_countries()`.
- `QgsField(k, QMetaType.Type(10))` (>= 33800) vs `QgsField(k, QVariant.String)`
  in `helpers.add_gbif_occ_to_layer()`.
