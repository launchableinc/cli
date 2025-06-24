"""Dependency injection utilities for Typer commands."""

from typing import Optional

from .app import Application

# Global application instance for dependency injection
_app_instance: Optional[Application] = None


def get_application() -> Application:
    """Dependency injection function for Application instance."""
    if _app_instance is None:
        raise RuntimeError("Application not initialized")
    return _app_instance


def set_application(app: Application) -> None:
    """Set the global application instance."""
    global _app_instance
    _app_instance = app
