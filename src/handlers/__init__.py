from fastapi import APIRouter
from . import comparators_handler, health_check, city_filter_extender_handler,minirules_comparators_handler

r = router = APIRouter(prefix="")

r.include_router(health_check.router)
r.include_router(comparators_handler.router)
r.include_router(minirules_comparators_handler.router)
r.include_router(city_filter_extender_handler.router)
