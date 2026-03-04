from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.redis import close_redis, get_redis


async def _ensure_default_user():
    """Create the default single-user account if it doesn't exist.

    Retries briefly to handle the race with alembic migrations on first boot.
    """
    import asyncio
    import logging

    from sqlmodel import select

    from app.api.deps import DEFAULT_USER_EMAIL
    from app.core.database import async_session_factory
    from app.models.user import User

    log = logging.getLogger(__name__)

    for attempt in range(10):
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(User).where(User.email == DEFAULT_USER_EMAIL)
                )
                if not result.scalar_one_or_none():
                    user = User(
                        email=DEFAULT_USER_EMAIL,
                        name="Aaron",
                        hashed_password="not-used",
                    )
                    session.add(user)
                    await session.commit()
                return
        except Exception:
            if attempt < 9:
                log.info("Waiting for database tables (attempt %d/10)...", attempt + 1)
                await asyncio.sleep(2)
            else:
                raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    get_redis()
    await _ensure_default_user()
    yield
    # Shutdown
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health_check():
    """Check application health including database and Redis connectivity."""
    # Check Redis
    redis_status = "ok"
    try:
        redis = get_redis()
        await redis.ping()
    except Exception:
        redis_status = "error"

    # Check Database
    db_status = "ok"
    try:
        from app.core.database import engine

        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception:
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" and redis_status == "ok" else "degraded",
        "database": db_status,
        "redis": redis_status,
    }
