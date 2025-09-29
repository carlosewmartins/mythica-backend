from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, personagem, campanha, historico
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": f"{settings.PROJECT_NAME} API está rodando!",
        "version": settings.VERSION
    }

app.include_router(auth.router, prefix="/api")
app.include_router(personagem.router, prefix="/api")
app.include_router(campanha.router, prefix="/api")
app.include_router(historico.router, prefix="/api")

