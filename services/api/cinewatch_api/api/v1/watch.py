"""Owner-only watch sessions and private media transport, governed by native Access."""
from __future__ import annotations

import base64
import json
import re
import secrets
import time
from pathlib import Path

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response, StreamingResponse

router = APIRouter(prefix="/watch", tags=["watch"])
SITE = "https://www.cinewatchtv.com"
GATEWAY = "https://cinewatch-owner-media-trial.cinewatchtv-stream.workers.dev"
OWNER = "cinewatchtv.stream@gmail.com"
COOKIE = "__Host-cinewatch-watch"
STATE_COOKIE = "__Host-cinewatch-watch-state"
HEADERS = {"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"}
DATA = Path(__file__).resolve().parents[2] / "watch"
ORIGINALS = json.loads((DATA / "originals.json").read_text())
RENDITIONS = json.loads((DATA / "renditions.json").read_text())


def failure(status: int = 403) -> Response:
    return JSONResponse({"error": "Playback unavailable"}, status_code=status, headers=HEADERS)


async def verified_owner(token: str, client: httpx.AsyncClient) -> int | None:
    """Native Cloudflare Access verifies signature, audience and identity on every request.

    Parsed expiry is only a local upper bound, never an authorization decision.
    The fixed HTTPS identity endpoint must independently affirm the exact owner.
    """
    try:
        if len(token) > 12000 or not re.fullmatch(r"[\w-]+\.[\w-]+\.[\w-]+", token):
            return None
        payload = token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        expiry = claims.get("exp")
        if type(expiry) is not int or expiry <= int(time.time()):
            return None
        result = await client.get(
            GATEWAY + "/identity", headers={"Cookie": "CF_Authorization=" + token},
            follow_redirects=False,
        )
        if result.status_code != 200 or result.headers.get("content-type", "").split(";")[0] != "application/json":
            return None
        identity = result.json()
        if identity != {"email": OWNER, "authorized": True}:
            return None
        return expiry
    except (ValueError, TypeError, AttributeError, httpx.HTTPError):
        return None


@router.get("/sign-in", operation_id="v1_watch_sign_in")
async def sign_in() -> Response:
    state = secrets.token_hex(32)
    response = RedirectResponse(GATEWAY + "/authorize?state=" + state, status_code=303, headers=HEADERS)
    response.set_cookie(STATE_COOKIE, state, httponly=True, secure=True, samesite="lax", max_age=300)
    return response


@router.post("/session", operation_id="v1_watch_session")
async def session(request: Request) -> Response:
    if request.headers.get("origin") != SITE:
        return failure()
    try:
        body = bytearray()
        async for part in request.stream():
            body.extend(part)
            if len(body) > 16000:
                return failure()
        data = json.loads(body)
        token, state = data.get("token"), data.get("state")
        if not isinstance(token, str) or not isinstance(state, str) or not re.fullmatch(r"[0-9a-f]{64}", state):
            return failure()
        if not secrets.compare_digest(request.cookies.get(STATE_COOKIE, ""), state):
            return failure()
        async with httpx.AsyncClient(timeout=10) as client:
            expiry = await verified_owner(token, client)
        if expiry is None:
            return failure()
        response = JSONResponse({"signedIn": True}, headers=HEADERS)
        response.set_cookie(COOKIE, token, httponly=True, secure=True, samesite="lax", max_age=min(900, expiry - int(time.time())))
        response.delete_cookie(STATE_COOKIE, httponly=True, secure=True, samesite="lax")
        return response
    except (ValueError, TypeError, AttributeError):
        return failure()


def watch_manifest(content_id: str) -> dict | None:
    item = ORIGINALS.get(content_id)
    if not item or not item["available"]:
        return None
    qualities = ["original"] + (["240p"] if content_id in RENDITIONS else [])
    return {
        "playableId": content_id, "title": item["title"],
        "kind": "clip" if "CLIP" in content_id else "episode", "episodeLabel": content_id,
        "sources": [{"id": q, "label": "Original" if q == "original" else "240p",
                     "mimeType": "video/mp4", "src": f"/api/cinewatch/watch/media/{content_id}/{q}"} for q in qualities],
        "subtitles": [], "capabilities": {"pictureInPicture": True, "playbackSpeed": True, "subtitles": False},
    }


@router.get("/manifest/{content_id}", operation_id="v1_watch_manifest")
async def manifest(content_id: str, request: Request) -> Response:
    async with httpx.AsyncClient(timeout=10) as client:
        if await verified_owner(request.cookies.get(COOKIE, ""), client) is None:
            return failure(401)
    result = watch_manifest(content_id)
    return JSONResponse(result, headers=HEADERS) if result else failure()


@router.get("/media/{content_id}/{quality}", operation_id="v1_watch_media")
@router.head("/media/{content_id}/{quality}", operation_id="v1_watch_media_head")
async def media(content_id: str, quality: str, request: Request) -> Response:
    item = ORIGINALS.get(content_id)
    if not item or not item["available"] or quality not in ("original", "240p") or (quality == "240p" and content_id not in RENDITIONS):
        return failure()
    token = request.cookies.get(COOKIE, "")
    client = httpx.AsyncClient(timeout=httpx.Timeout(120, connect=10), follow_redirects=False)
    upstream = None
    try:
        if await verified_owner(token, client) is None:
            await client.aclose()
            return failure(401)
        headers = {"Cookie": "CF_Authorization=" + token}
        if request.headers.get("range"):
            if not re.fullmatch(r"bytes=(\d*)-(\d*)", request.headers["range"]):
                await client.aclose()
                return failure(416)
            headers["Range"] = request.headers["range"]
        upstream = await client.send(client.build_request(request.method, f"{GATEWAY}/media/{content_id}/{quality}", headers=headers), stream=True)
        if upstream.status_code not in (200, 206, 416) or (upstream.status_code in (200, 206) and not upstream.headers.get("content-type", "").startswith("video/mp4")):
            await upstream.aclose()
            await client.aclose()
            return failure()
        out = dict(HEADERS, **{"Cross-Origin-Resource-Policy": "same-origin"})
        for name in ("Content-Type", "Content-Length", "Content-Range", "Accept-Ranges"):
            if upstream.headers.get(name):
                out[name] = upstream.headers[name]
        if request.method == "HEAD":
            status = upstream.status_code
            await upstream.aclose()
            await client.aclose()
            return Response(status_code=status, headers=out)
        async def stream():
            try:
                async for chunk in upstream.aiter_raw():
                    yield chunk
            finally:
                await upstream.aclose()
                await client.aclose()
        return StreamingResponse(stream(), status_code=upstream.status_code, headers=out)
    except httpx.HTTPError:
        if upstream:
            await upstream.aclose()
        await client.aclose()
        return failure(503)
