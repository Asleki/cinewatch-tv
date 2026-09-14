"""Composition root for versioned V1 routes."""

from fastapi import APIRouter

from cinewatch_api.api.v1.catalog import router as catalog_router
from cinewatch_api.api.v1.home import router as home_router
from cinewatch_api.api.v1.home_experience import router as home_experience_router
from cinewatch_api.api.v1.system import router as system_router

router = APIRouter()
router.include_router(system_router)
router.include_router(catalog_router)
router.include_router(home_router)
router.include_router(home_experience_router)
