from .auth import auth_router
from .dashboard import dashboard_router
from .health import health_router
from .profiles import profiles_router
from .searches import searches_router
from .signals import signals_router
from .users import users_router

__all__ = [
    "auth_router",
    "dashboard_router",
    "health_router",
    "profiles_router",
    "searches_router",
    "signals_router",
    "users_router",
]
