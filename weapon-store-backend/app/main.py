from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.ai import router as ai_router
from app.routers.auth import router as auth_router
from app.routers.cart import router as cart_router
from app.routers.catalog import router as catalog_router
from app.routers.orders import router as orders_router
from app.routers.users import router as users_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.2.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(catalog_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok", "environment": settings.APP_ENV}
