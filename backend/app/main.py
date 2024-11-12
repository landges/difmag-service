import logging
from fastapi import FastAPI, Request, Response, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.const import (
    OPEN_API_DESCRIPTION,
    OPEN_API_TITLE,
)
from app.routers import (
    images
)
import os
from app.version import __version__
from app.core.config import config
from sqlalchemy.orm import Session
import uvicorn

APP_NAME = os.environ.get("APP_NAME", "app")


app = FastAPI(
    title=OPEN_API_TITLE,
    description=OPEN_API_DESCRIPTION,
    version=__version__,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)
if not config.debug:
    # Filter out /endpoint
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


#TODO get from env
origins = [
    "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_router = APIRouter(prefix="/api")

@app.get("/health")
def healthcheck():
    return Response(status_code=200)

api_router.include_router(images.router)


app.include_router(api_router)
