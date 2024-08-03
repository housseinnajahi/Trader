import logging
import threading

from fastapi import FastAPI

from .redis import redis_subscriber
from .router import router


def create_application() -> FastAPI:
    application = FastAPI(openapi_url="/lstm/openapi.json", docs_url="/lstm/docs")
    application.include_router(router, prefix="/api/v1", tags=["lstm"])
    return application


app = create_application()
log = logging.getLogger("uvicorn")


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]
    log.info(url_list)
    threading.Thread(target=redis_subscriber).start()


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
