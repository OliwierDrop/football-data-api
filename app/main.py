import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, health, home, matches, standings, teams
from app.config import settings
from app.services.scheduler import start_scheduler, stop_scheduler

from app.utils.names import clean_team_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Football Data API",
    description=(
        "REST API for football data scraped from 90minut.pl. "
        "Serves PostgreSQL data only – scraping never happens on user requests."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(matches.router)
app.include_router(standings.router)
app.include_router(teams.router)
app.include_router(home.router)
app.include_router(admin.router)


@app.get("/")
def root() -> dict:
    return {
        "service": "football-data-api",
        "team": clean_team_name(settings.team_name),
        "docs": "/docs",
    }
