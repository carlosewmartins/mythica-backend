from fastapi import FastAPI
from app.api.routes import auth, personagem
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.include_router(auth.router, prefix="/api")
app.include_router(personagem.router, prefix="/api")