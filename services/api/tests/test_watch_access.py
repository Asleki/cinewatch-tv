"""Private watch authorization regressions; fixtures never grant public rights."""
import asyncio
import base64
import json
import time

import httpx
import pytest

from cinewatch_api.api.v1.watch import GATEWAY, OWNER, verified_owner, watch_manifest


def token(expiry):
    payload = base64.urlsafe_b64encode(json.dumps({"exp": expiry}).encode()).decode().rstrip("=")
    return "e30." + payload + ".ZmFrZQ"


def run_verification(value, response):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: response)) as client:
            return await verified_owner(value, client)
    return asyncio.run(run())


def test_native_access_owner_confirmation_required():
    expiry = int(time.time()) + 60
    assert run_verification(token(expiry), httpx.Response(200, json={"email": OWNER, "authorized": True})) == expiry


@pytest.mark.parametrize("response", [
    httpx.Response(302, headers={"location": GATEWAY + "/login"}),
    httpx.Response(403, json={"email": OWNER, "authorized": True}),
    httpx.Response(200, text="Login", headers={"content-type": "text/html"}),
    httpx.Response(200, json={"email": "other@example.com", "authorized": True}),
    httpx.Response(200, json={"email": OWNER, "authorized": False}),
])
def test_native_access_rejection_cannot_become_session(response):
    assert run_verification(token(int(time.time()) + 60), response) is None


@pytest.mark.parametrize("value", ["", "bad", "a.b.c", "a" * 12001, token(0), token("tomorrow"), "e30.W10.ZmFrZQ", "e30.bnVsbA.ZmFrZQ"])
def test_malformed_and_expired_tokens_denied(value):
    assert run_verification(value, httpx.Response(200, json={"email": OWNER, "authorized": True})) is None


@pytest.mark.parametrize("content_id", ["S02E15", "S02E16", "S02E17", "S02E18", "../S02E01"])
def test_restricted_and_unknown_media_denied(content_id):
    assert watch_manifest(content_id) is None


def test_trailer_and_episode_use_same_origin_private_transport():
    for content_id in ["S02_CLIP03", "S02E01", "S02E14"]:
        manifest = watch_manifest(content_id)
        assert manifest["sources"][0]["src"] == f"/api/cinewatch/watch/media/{content_id}/original"
        assert "r2.cloudflarestorage.com" not in json.dumps(manifest)
        assert "sha256" not in json.dumps(manifest)

from fastapi import FastAPI
from fastapi.testclient import TestClient
from cinewatch_api.api.v1 import watch


def client():
    app = FastAPI()
    app.include_router(watch.router, prefix='/api/v1')
    return TestClient(app, base_url=watch.SITE)


def test_sign_in_nonce_cookie_secure_and_gateway_fixed():
    with client() as browser:
        response = browser.get('/api/v1/watch/sign-in', follow_redirects=False)
        assert response.status_code == 303
        assert response.headers['location'].startswith(GATEWAY + '/authorize?state=')
        cookie = response.headers['set-cookie'].lower()
        assert 'secure' in cookie and 'httponly' in cookie and 'samesite=lax' in cookie
        assert 'path=/' in cookie


@pytest.mark.parametrize('body,origin', [
    ({'token': 'x', 'state': 'a' * 64}, 'https://other.example'),
    ({'token': 'x', 'state': 'a' * 64}, watch.SITE),
    ({'token': 'x', 'state': 'bad'}, watch.SITE),
    ([], watch.SITE),
])
def test_session_cannot_skip_origin_and_nonce(body, origin):
    with client() as browser:
        response = browser.post('/api/v1/watch/session', json=body, headers={'Origin': origin})
        assert response.status_code == 403
        assert watch.COOKIE not in response.cookies


def test_valid_session_requires_owner_gate_and_caps_lifetime(monkeypatch):
    async def allow(token, transport):
        assert token == 'fixture'
        return int(time.time()) + 3600
    monkeypatch.setattr(watch, 'verified_owner', allow)
    with client() as browser:
        start = browser.get('/api/v1/watch/sign-in', follow_redirects=False)
        nonce = start.cookies[watch.STATE_COOKIE]
        response = browser.post('/api/v1/watch/session', json={'token': 'fixture', 'state': nonce}, headers={'Origin': watch.SITE})
        assert response.status_code == 200
        assert response.cookies[watch.COOKIE] == 'fixture'
        assert 'Max-Age=900' in response.headers['set-cookie']
        assert response.headers['Cache-Control'] == 'private, no-store'


def test_manifest_without_session_denied():
    with client() as browser:
        response = browser.get('/api/v1/watch/manifest/S02E01')
        assert response.status_code == 401
        assert 'sources' not in response.json()


def test_restricted_media_denied_before_storage_access():
    with client() as browser:
        for content in ['S02E15', 'S02E16', 'S02E17']:
            assert browser.get(f'/api/v1/watch/media/{content}/original').status_code == 403


def test_private_proxy_forwards_range_and_only_safe_headers(monkeypatch):
    original_client = httpx.AsyncClient
    seen = []
    def handle(request):
        seen.append(request)
        if request.url.path == '/identity':
            return httpx.Response(200, json={'email': OWNER, 'authorized': True})
        assert request.url.host == 'cinewatch-owner-media-trial.cinewatchtv-stream.workers.dev'
        assert request.headers['range'] == 'bytes=8-23'
        return httpx.Response(206, headers={'Content-Type': 'video/mp4', 'Content-Range': 'bytes 8-23/100', 'Accept-Ranges': 'bytes', 'Set-Cookie': 'must-not-leak=x'}, stream=httpx.ByteStream(b'0123456789abcdef'))
    monkeypatch.setattr(watch.httpx, 'AsyncClient', lambda **kwargs: original_client(transport=httpx.MockTransport(handle), **kwargs))
    with client() as browser:
        browser.cookies.set(watch.COOKIE, token(int(time.time()) + 60))
        response = browser.get('/api/v1/watch/media/S02E01/original', headers={'Range': 'bytes=8-23'})
    assert response.status_code == 206 and response.content == b'0123456789abcdef'
    assert response.headers['Content-Range'] == 'bytes 8-23/100'
    assert 'Set-Cookie' not in response.headers
    assert response.headers['Cache-Control'] == 'private, no-store'
    assert len(seen) == 2


@pytest.mark.parametrize('status,content_type', [(302, 'text/html'), (200, 'text/html'), (403, 'video/mp4')])
def test_proxy_never_treats_access_login_or_denial_as_video(monkeypatch, status, content_type):
    original_client = httpx.AsyncClient
    def handle(request):
        if request.url.path == '/identity':
            return httpx.Response(200, json={'email': OWNER, 'authorized': True})
        return httpx.Response(status, headers={'Content-Type': content_type, 'Location': 'https://other.example'}, stream=httpx.ByteStream(b'not-video'))
    monkeypatch.setattr(watch.httpx, 'AsyncClient', lambda **kwargs: original_client(transport=httpx.MockTransport(handle), **kwargs))
    with client() as browser:
        browser.cookies.set(watch.COOKIE, token(int(time.time()) + 60))
        response = browser.get('/api/v1/watch/media/S02E01/original')
    assert response.status_code == 403
    assert b'not-video' not in response.content
