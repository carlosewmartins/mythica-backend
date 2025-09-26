from datetime import datetime, timedelta
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from bson import ObjectId
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.db.database import users_list

password_config = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
ALGORITHM = settings.ALGORITHM

# Faz hash da senha do usuario
def hash_password(password: str):
    return password_config.hash(password)

# Verifica senha plena com hash armazenada
def verify_password(plain: str, hashed: str):
    return password_config.verify(plain, hashed)

# Busca de usuario por email
def get_user_by_email(email: str):
    return users_list.find_one({"email": email})

# Busca de usuario por id
def get_user_by_id(user_id: str):
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    return users_list.find_one({"_id": oid})

# JWT
# Cria token de acesso
def create_access_token(subject: str):
    expire = datetime.now() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    payload = {"sub": subject, "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

# Decifra token de acesso
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado", headers={"WWW-Authenticate": "Bearer"})
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido", headers={"WWW-Authenticate": "Bearer"})

# Valida token e usuario para proteção de rotas
def get_current_user(token: str):
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido", headers={"WWW-Authenticate": "Bearer"})
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado", headers={"WWW-Authenticate": "Bearer"})
    return {"id": str(user["_id"]), "name": user["name"], "email": user["email"]}
