import logging

from fastapi import Depends, FastAPI, HTTPException, status  # noqa
from fastapi.responses import JSONResponse  # noqa
from fastapi.middleware.cors import CORSMiddleware
from requests import Session

from routes import countries_router
from utils import get_session, init_db
from services import CountryService

logging.basicConfig(
    format="%(asctime)s : %(levelname)s - %(message)s",
    level=logging.DEBUG, filename="out.log")


# main application entry point
app = FastAPI(
    title="HNG 13",
    description="stage 2 backend track",
)


@app.on_event("startup")
def on_startup():
    init_db()


# CORS Management
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(
    router=countries_router
)


@app.get(
        "/status",
        status_code=status.HTTP_200_OK)
async def get_status(session: Session = Depends(get_session)):
    try:
        stat = CountryService.get_country_status(session=session)
        return {
            "total_countries": stat[0],
            "last_refreshed_at": (stat[1]).last_refreshed_at
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
