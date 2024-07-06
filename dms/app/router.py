from fastapi import APIRouter

from .tickers.apis.tickers import router as tickers_router

router = APIRouter()

router.include_router(tickers_router, prefix="/tickers", tags=["tickers"])
