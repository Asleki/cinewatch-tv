"""Composition root for versioned V1 routes."""

from fastapi import APIRouter

from cinewatch_api.api.v1.catalog import router as catalog_router
from cinewatch_api.api.v1.external import router as external_router
from cinewatch_api.api.v1.home import router as home_router
from cinewatch_api.api.v1.home_experience import router as home_experience_router
from cinewatch_api.api.v1.news import router as news_router
from cinewatch_api.api.v1.search import router as search_router
from cinewatch_api.api.v1.system import router as system_router
from cinewatch_api.api.v1.voice import router as voice_router

router = APIRouter()
router.include_router(system_router)
router.include_router(catalog_router)
router.include_router(external_router)
router.include_router(home_router)
router.include_router(home_experience_router)
router.include_router(search_router)
router.include_router(news_router)
router.include_router(voice_router)
