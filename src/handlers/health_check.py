from fastapi import APIRouter
from starlette.responses import JSONResponse

from src.utils.logger import logger

router = APIRouter(tags=["health-check"])


@router.get("/health-check")
async def health_check() -> JSONResponse:
    """
    Health check сервиса
    """
    await logger.info("Requested health-check")
    return JSONResponse({"success": True, "message": "All clear, Schipper"})
