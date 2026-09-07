"""Composition root for versioned V1 routes."""

from fastapi import APIRouter

from cinewatch_api.api.v1.system import router as system_router

router = APIRouter()
router.include_router(system_router)
