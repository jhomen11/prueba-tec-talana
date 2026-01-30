from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie # <--- Usamos este esquema
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.modules.users.repository import UserRepository
from app.modules.users.models import User

# Esto le dice a Swagger UI que la seguridad depende de una cookie llamada "access_token"
cookie_scheme = APIKeyCookie(name="access_token")

def get_current_user(
    token: str = Depends(cookie_scheme), 
    db: Session = Depends(get_db)
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
    )
    
    try:
        # Nota: En cookies generalmente guardamos el token puro, sin el prefijo "Bearer "
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email)
    if user is None:
        raise credentials_exception
        
    return user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="No tienes permisos de administrador"
        )
    return current_user