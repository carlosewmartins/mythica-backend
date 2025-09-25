from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # ===== APP SETTINGS =====
    PROJECT_NAME: str
    VERSION: str

    # ===== SECURITY =====
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # ===== DATABASE =====
    MONGODB_URL: str
    DATABASE_NAME: str

    # ===== CORS =====
    CORS: str

    class Config:
        env_file = "../../.env"

# Instância global das configurações
settings = Settings()

def print_startup_info():
    print("=" * 50)
    print(f"🏰 {settings.PROJECT_NAME} v{settings.VERSION}")
    print("=" * 50)
    print(f"🗄️ Database: {settings.DATABASE_NAME}")
    print(f"🌐 CORS : {len(settings.CORS)} configurado")
    print(f"🔐 JWT expira em: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
    print("=" * 50)

print_startup_info()