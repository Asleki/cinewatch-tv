#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"

REQUIRED = (
    "apps/web/package.json",
    "apps/web/next-env.d.ts",
    "apps/web/next.config.ts",
    "apps/web/tsconfig.json",
    "apps/web/eslint.config.mjs",
    "apps/web/src/app/layout.tsx",
    "apps/web/src/app/page.tsx",
    "apps/web/src/app/loading.tsx",
    "apps/web/src/app/not-found.tsx",
    "apps/web/src/app/error.tsx",
    "apps/web/src/app/global-error.tsx",
    "apps/web/src/app/robots.ts",
    "apps/web/src/app/manifest.ts",
    "apps/web/src/lib/config/public-env.ts",
    "apps/web/src/lib/api/system-client.ts",
    "apps/web/public/brand/.gitkeep",
    "apps/web/public/icons/.gitkeep",
    "apps/web/public/seo/.gitkeep",
)

EXPECTED_RUNTIME = {
    "@cinewatch/contracts": "0.0.0",
    "next": "16.3.4",
    "react": "19.2.8",
    "react-dom": "19.2.8",
}
EXPECTED_DEV = {
    "@types/node": "24.13.3",
    "@types/react": "19.2.18",
    "@types/react-dom": "19.2.7",
    "eslint": "9.39.5",
    "eslint-config-next": "16.3.4",
    "typescript": "6.0.3",
}
FORBIDDEN_DEPENDENCIES = {
    "axios",
    "tailwindcss",
    "@tailwindcss/postcss",
    "@tmdb",
    "@auth0",
    "next-auth",
    "@aws-sdk/client-cognito-identity-provider",
}
FORBIDDEN_SOURCE_MARKERS = (
    "api.themoviedb.org",
    "youtube.googleapis.com",
    "TMDB_API_KEY",
    "YOUTUBE_API_KEY",
)


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail("missing frontend skeleton paths: " + ", ".join(missing))

    if (WEB / "src" / "app" / "api").exists():
        fail("Next.js API route boundary is forbidden; FastAPI owns application APIs")

    package = load_json(WEB / "package.json")
    if package.get("dependencies") != EXPECTED_RUNTIME:
        fail("unexpected frontend runtime dependency authority")
    if package.get("devDependencies") != EXPECTED_DEV:
        fail("unexpected frontend development dependency authority")

    all_dependencies = set(package.get("dependencies", {})) | set(package.get("devDependencies", {}))
    forbidden = sorted(all_dependencies & FORBIDDEN_DEPENDENCIES)
    if forbidden:
        fail("forbidden premature frontend dependencies: " + ", ".join(forbidden))

    scripts = package.get("scripts", {})
    if scripts.get("build") != "next build --webpack":
        fail("frontend production build must use the qualified webpack fallback")
    if scripts.get("lint") != "eslint .":
        fail("frontend lint authority must use ESLint CLI")
    if scripts.get("typecheck") != "tsc --noEmit":
        fail("frontend typecheck authority must use tsc --noEmit")

    tsconfig = load_json(WEB / "tsconfig.json")
    compiler = tsconfig.get("compilerOptions", {})
    if compiler.get("strict") is not True:
        fail("TypeScript strict mode must remain enabled")
    if compiler.get("moduleResolution") != "bundler":
        fail("TypeScript moduleResolution must remain bundler")
    if compiler.get("types") != ["node"]:
        fail("TypeScript 6 ambient Node types must be explicit")

    robots = (WEB / "src/app/robots.ts").read_text(encoding="utf-8")
    if 'disallow: "/"' not in robots:
        fail("V1 robots policy must disallow the entire private-beta site")

    env_template = (ROOT / ".env.example").read_text(encoding="utf-8")
    for name in ("NEXT_PUBLIC_CINEWATCH_API_BASE_URL", "NEXT_PUBLIC_CINEWATCH_SITE_URL"):
        if name not in env_template:
            fail(f"missing public frontend environment key: {name}")
    if re.search(r"NEXT_PUBLIC_[A-Z0-9_]*(?:SECRET|PASSWORD|TOKEN|API_KEY)", env_template):
        fail("secret-like value must never use NEXT_PUBLIC_ prefix")

    source_files = list((WEB / "src").rglob("*.ts")) + list((WEB / "src").rglob("*.tsx"))
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in source_files)
    markers = [marker for marker in FORBIDDEN_SOURCE_MARKERS if marker in source_text]
    if markers:
        fail("frontend source contains forbidden provider authority markers: " + ", ".join(markers))

    for directory in (WEB / "public/brand", WEB / "public/icons", WEB / "public/seo"):
        actual = sorted(path.name for path in directory.iterdir())
        if actual != [".gitkeep"]:
            fail(f"{directory.relative_to(ROOT)} must reserve location only until V1.3")

    print("PASS  frontend skeleton paths")
    print("PASS  Next.js and React dependency authority")
    print("PASS  TypeScript 6 strict configuration")
    print("PASS  FastAPI remains application API authority")
    print("PASS  private-beta robots and public-env policy")
    print("PASS  asset locations reserved without premature brand assets")
    print("PASS  CWTV.V1.2.4 frontend skeleton policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
