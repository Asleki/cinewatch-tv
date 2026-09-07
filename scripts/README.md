# Repository Scripts

Repository-level deterministic engineering and qualification scripts live here.

Scripts must remain usable from Termux where the required runtime exists. Platform-specific production build checks may run only in authoritative Linux CI when Android native tooling is unavailable.

Current backend checks:

- `python scripts/check_backend_skeleton.py` validates the V1.2.3 source/dependency boundary without importing FastAPI;
- `bash scripts/check_backend_runtime.sh` runs compile, service tests, a temporary local Uvicorn server, and live health/status/request-ID probes using `services/api/.venv`.
