"""ASGI entry point for CineWatch TV."""

from cinewatch_api.application import create_app

app = create_app()
