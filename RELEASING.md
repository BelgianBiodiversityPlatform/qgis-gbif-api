# Releasing the GBIF Occurrences plugin

This plugin is packaged and published with
[qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci). A release is
triggered by **publishing a GitHub Release**; GitHub Actions then builds the
zip, attaches it to that release, and publishes the plugin to the official QGIS
plugin repository at [plugins.qgis.org](https://plugins.qgis.org).

> Why a GitHub Release and not just a tag: qgis-plugin-ci does **not** create the
> GitHub Release itself - it only attaches the zip to a release that already
> exists. Publishing the release (which also creates the tag) is what provides
> that release and triggers the workflow. A bare `git push` of a tag creates no
> release, so the job would fail with `GithubReleaseNotFound`.

## Repository layout

The plugin source lives in the `GBIFOccurrences/` subdirectory (the folder that
contains `metadata.txt`). qgis-plugin-ci uses that folder name for both the zip
file and the installed plugin folder in QGIS, so it must stay `GBIFOccurrences`
to keep existing users' installations working across upgrades. Everything at the
repository root (this file, the README, screenshots, the workflow, the
`tests/`) is development tooling and is **not** shipped inside the plugin zip.

## One-time setup

The automated publish needs your OSGeo (plugins.qgis.org) credentials, stored as
GitHub Actions secrets. In the GitHub repository, go to
**Settings -> Secrets and variables -> Actions** and add:

| Secret name      | Value                                              |
| ---------------- | -------------------------------------------------- |
| `OSGEO_USERNAME` | Your OSGeo / plugins.qgis.org account username     |
| `OSGEO_PASSWORD` | The matching password                              |

`GITHUB_TOKEN` is provided automatically by GitHub Actions - you do not create
it. The account behind `OSGEO_USERNAME` must have maintainer rights on the
plugin at plugins.qgis.org, otherwise the upload step is rejected.

## Cutting a release

1. **Bump the version and changelog** in
   [`GBIFOccurrences/metadata.txt`](GBIFOccurrences/metadata.txt):
   - update `version=` (e.g. `version=0.4.1`)
   - add a matching entry at the top of the `changelog=` block
   Commit this on a branch and merge it to `master` as usual.

2. **Publish a GitHub Release** whose tag is the bare version number (no `v`
   prefix). The release creates the tag for you, so do this from up-to-date
   `master`:

   ```bash
   git checkout master && git pull
   gh release create 0.4.1 --title 0.4.1 --generate-notes
   ```

   (You can also use the GitHub UI: **Releases -> Draft a new release**, create
   a new tag `0.4.1` targeting `master`, then **Publish release**.)

   The tag string is written verbatim into `metadata.txt` as the plugin version
   by qgis-plugin-ci, which is why we use `0.4.1` and not `v0.4.1`. Keep the tag
   identical to the `version=` value you set in step 1.

3. **Watch the workflow.** Publishing the release triggers
   [`.github/workflows/release.yaml`](.github/workflows/release.yaml). When it
   finishes you should have:
   - a new GitHub release with the plugin `.zip` attached, and
   - the new version live on plugins.qgis.org (allow a few minutes for it to
     appear, and note that the QGIS team may hold a first-ever submission for
     manual approval).

## Building the zip locally (for testing)

To produce and test the zip before tagging a real release, see the
[Build the plugin zip locally](CONTRIBUTING.md#build-the-plugin-zip-locally)
section in CONTRIBUTING.md.

## Manual fallback

If you ever need to publish without CI (e.g. the workflow is broken), the same
tool does everything locally (run it through the uv-managed environment - see
CONTRIBUTING.md):

```bash
uv run qgis-plugin-ci release 0.4.1 \
  --osgeo-username "$OSGEO_USERNAME" \
  --osgeo-password "$OSGEO_PASSWORD"
```

Omit the OSGeo flags to only build the zip without touching plugins.qgis.org.

Add `--github-token "$GITHUB_TOKEN"` to also attach the zip to a GitHub Release
- but note that release must **already exist** for the tag (create it first with
`gh release create 0.4.1`), because qgis-plugin-ci attaches to an existing
release rather than creating one.
