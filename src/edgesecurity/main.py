from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI

from edgesecurity.api.auth import router as auth_router
from edgesecurity.database import init_db

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Initializing Edge Security Database")
    await init_db()
    yield

app = FastAPI(
    title="Edge Security API",
    description="Zero Trust Gateway and Identity Provider for Edge Devices",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_router, prefix="/api/v1")

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}

def start() -> None:
    uvicorn.run("edgesecurity.main:app", host="0.0.0.0", port=8001, reload=True)

if __name__ == "__main__":
    start()
