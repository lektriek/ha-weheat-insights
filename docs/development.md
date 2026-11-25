# Development

## Python

```bash
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python -r requirements_test.txt
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/pytest
```

The calculation logic lives in `custom_components/weheat_insights/calculations/`
as pure functions with no Home Assistant imports, so it can be tested with
plain fixture data.

## Frontend

The dashboard strategy is TypeScript in `frontend/src/`, bundled with esbuild
into `custom_components/weheat_insights/www/weheat-insights.js`. The bundle is
committed so HACS users need no build step; CI fails if it is out of date.

```bash
cd frontend
npm ci
npm run check   # typecheck + build
```

Rebuild and commit the bundle with every frontend change.

## Local Home Assistant

```bash
docker compose up -d
```

Open <http://localhost:8123>, finish onboarding, then:

1. Add the core **Weheat** integration and sign in with your Weheat account.
2. Add **Weheat Insights** and pick your heat pump.
3. Create a new dashboard from scratch, open the raw configuration editor and use:

   ```yaml
   strategy:
     type: custom:weheat-insights
   ```

The integration directory is mounted read-only into the container. After a
Python change, restart Home Assistant (`docker compose restart`). After a
frontend change, rebuild the bundle and hard-refresh the browser.

`dev/config/` holds the instance's state and is ignored by git, except for
`configuration.yaml`.

## Releasing

Versions follow [semantic versioning](https://semver.org/). HACS and the Home
Assistant Marketplace offer a new version only when it is published as a GitHub
release, and show the release notes when offering the update.

1. While working, add each user-visible change under **Unreleased** in
   [CHANGELOG.md](../CHANGELOG.md), as *Added*, *Changed*, *Fixed* or *Removed*.
2. To release, run `scripts/release.py 1.2.0` on an up-to-date `main`. It sets
   the version in `manifest.json`, `pyproject.toml` and `frontend/package.json`
   with its lock file, dates the changelog section, commits `Release 1.2.0` and
   tags `v1.2.0`. It pushes nothing.
3. Push the commit and tag with the command it prints. The **Release**
   workflow checks that the tag matches the manifest and publishes the GitHub
   release with that version's changelog section as notes.

A version with a suffix, such as `1.3.0-beta.1`, becomes a pre-release; HACS
only offers it to users who switched on *Show beta versions*. Don't create
releases in the GitHub web interface: the workflow then fails because the
release already exists, and the notes don't come from the changelog.

[ha-weheat-control](https://github.com/lektriek/ha-weheat-control) uses the
same process, script and workflow.
