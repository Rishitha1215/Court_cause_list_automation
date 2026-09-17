"""
FastAPI application.

Provides the CAPTCHA web bridge together with the
existing application API routes.
"""

from fastapi import FastAPI

from app.api import (
    routes_admin,
    routes_advocates,
    routes_auth,
    routes_cases,
)

from app.config import settings

from app.database import Base, engine

from app.routes.captcha import router as captcha_router

import app.models  # noqa: F401


def create_app() -> FastAPI:

    app = FastAPI(
        title=settings.app_name,
    )

    # ----------------------------------------------------------
    # CAPTCHA routes
    # ----------------------------------------------------------

    app.include_router(
        captcha_router
    )

    # ----------------------------------------------------------
    # Database
    # ----------------------------------------------------------

    Base.metadata.create_all(
        bind=engine
    )

    # ----------------------------------------------------------
    # Existing API routes
    # ----------------------------------------------------------

    app.include_router(
        routes_auth.router
    )

    app.include_router(
        routes_advocates.router
    )

    app.include_router(
        routes_cases.router
    )

    app.include_router(
        routes_admin.router
    )

    # ----------------------------------------------------------
    # Health check
    # ----------------------------------------------------------

    @app.get(
        "/health",
        tags=["health"],
    )
    def health():

        return {
            "status": "ok",
            "app": settings.app_name,
        }

    return app


app = create_app()