from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import factions, maps, routes, rovers, stations
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_database()
    yield


app = FastAPI(
    title="Moon Rover Control Center API",
    description="Бэкенд для мониторинга и управления лунными роверами",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stations.router, prefix="/api")
app.include_router(rovers.router, prefix="/api")
app.include_router(maps.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(factions.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Lunar API is running"}