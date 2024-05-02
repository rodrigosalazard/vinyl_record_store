from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)

from jose import JWTError, jwt

from passlib.context import CryptContext
from pydantic import ValidationError
from typing_extensions import Annotated
from datetime import datetime, timedelta
from typing import List, Union

from cruds import users
from schemas.User import UserInDB
from schemas.Token import TokenData
from schemas.User import User
from cruds import vars as crud_vars
from database.connection import SessionLocal, engine

# SECRET_KEY = crud_vars.getValue("SECRET_KEY")
# ALGORITHM = crud_vars.getValue("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(crud_vars.getValue("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"user": "Read and update information about the current user and CRUD Discs.","admin": "CRUD information about the users and discs."},
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


users_db = []

# Set para almacenar tokens inválidos
blacklist = set()

# This method define a global var to load users from database users_db
def load_users():
    global users_db
    users_db = get_users_db

# This method loads the users from the database
def get_users_db():
    db = SessionLocal()
    return users.get_users(db, skip=0, limit=200)

# This method verify password using CryptContext
def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)

# This method get hash from password
def get_password_hash(password):
    return pwd_context.hash(password)

# This method search the email of user in data base to check if exists
def search_user(users, email: str):
    for user in users:
        if user.email == email:
            object_dict = vars(user)
            return UserInDB(**object_dict)

# This method autenticated the user if exists and the password match with thats stored
def authenticate_user(fake_db, email: str, password: str):
    user = search_user(fake_db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

#Create a random secret key that will be used to sign the JWT tokens.
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    secret_key = crud_vars.getValue("SECRET_KEY")
    algorithm = crud_vars.getValue("ALGORITHM")
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

#  Esta función es responsable de obtener y validar el token de autenticación enviado por el cliente y devolver el usuario correspondiente.
async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]):
    '''
    Actualiza para recibir el mismo token que antes, pero esta vez, utilizando tokens JWT.

    Decodifica el token recibido, verifícalo y devuelve el usuario actual.

    Si el token no es válido, devuelve un error HTTP inmediatamente.
    '''
    if token in blacklist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )
    try:
        secret_key = crud_vars.getValue("SECRET_KEY")
        algorithm = crud_vars.getValue("ALGORITHM")
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials by username:"+username,
            headers={"WWW-Authenticate": authenticate_value},
        )
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, email=username)
    except (JWTError, ValidationError):
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )
        raise credentials_exception
    users_db = get_users_db()
    user = search_user(users_db, email=token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials by username:"+str(token_data.email),
            headers={"WWW-Authenticate": authenticate_value},
        )
    for scope in security_scopes.scopes: #check logic of this change xD
        if scope not in token_data.scopes: #check logic of this change xD
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                # detail='No tienes suficientes permisos. Only authorized personnel for '+security_scopes.scope_str+' users',
                detail='No tienes suficientes permisos :( Only for: '+scope,
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

#Esta función es una dependencia que se usa en otras rutas para asegurar que el usuario que intenta acceder a la ruta está activo. 
async def get_current_active_user(current_user: Annotated[User, Security(get_current_user, scopes=["user"])]):
    if current_user.deletad_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario Inactivo")
    return current_user
