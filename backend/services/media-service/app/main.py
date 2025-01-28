from app.api.endpoints.media_route import media_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import logging
from fastapi.staticfiles import StaticFiles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)

logger = logging.getLogger(__name__)
logger.info("Custom logging is configured.")

app = FastAPI()

# app.mount("/static", StaticFiles(directory="D:/Software Systems Analysis & Design/MailService_Project/project/backend/services/media-service/app/static"), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(media_router, prefix="/media", tags=["media"])

logger.info("Media Service Started")


@app.get("/")
async def root():
    return {"message": "Hello From Media Service !"}