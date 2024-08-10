import logging

from fastapi import FastAPI
from fastapi_utilities import repeat_every

from .postgres import postgres
from .router import router
from .tickers import models
from .tickers.services.polygon_service import polygon_client


def create_application() -> FastAPI:
    application = FastAPI(openapi_url="/dms/openapi.json", docs_url="/dms/docs")
    application.include_router(router, prefix="/api/v1", tags=["dms"])
    models.postgres.base.metadata.create_all(bind=postgres.engine)
    return application


app = create_application()
log = logging.getLogger("uvicorn")


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]
    log.info(url_list)
    # polygon_client.get_aggregations()


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


@app.on_event("startup")
@repeat_every(seconds=60)
async def get_tickers_info_from_polygon():
    polygon_client.get_tickers()


@app.on_event("startup")
@repeat_every(seconds=15)
async def get_aggregations_from_polygon():
    polygon_client.get_aggregations()
