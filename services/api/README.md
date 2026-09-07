# CineWatch TV API Service

This directory is the governed CineWatch TV FastAPI backend service boundary.

`CWTV.V1.2.3` introduces only the backend service skeleton: application factory, settings, JSON logging bootstrap, request IDs, error envelopes, health/status routes, V1 routing boundary, and automated service tests.

It does not introduce database schemas, authentication, providers, rights, playback, Discover, Watch, Explore, My CineWatch, cinema, or NexVox features.

## Termux development setup

Run from the repository root:

```bash
python -m venv services/api/.venv
. services/api/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e 'services/api[test]'
```

Do not install the `quality` extra on Android/Termux. Linux CI owns Ruff qualification because the required Android Ruff binary path is not available.

## Tests

```bash
python -m pytest services/api/tests -q
```

## Run locally

```bash
python -m uvicorn cinewatch_api.main:app   --app-dir services/api   --host 127.0.0.1   --port 8000
```

Then inspect `/health`, `/status`, `/api/v1/status`, and `/docs` on the local server.

The root `.env` file may override the public non-secret defaults defined in `.env.example`.
