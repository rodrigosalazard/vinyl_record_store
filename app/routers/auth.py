from fastapi import Depends, FastAPI, HTTPException, Security, status, Request, Response, Cookie, File, UploadFile, Form, APIRouter
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from datetime import datetime, timedelta, date
from database.connection import SessionLocal
from schemas.Token import Token
from schemas.User import UserSignIn
from auth import auth
from cruds import users
from cruds import vars as crud_vars

router = APIRouter(
    # prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found Route"}},
)

@router.post("/token", response_model=Token)
async def access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):  
    """
    Crear un token de acceso JWT real y lo regresa
    :param None: None
    :type None: None

    :return: El schema de un Token
    :rtype: Token

    :raises HTTPException: HTTP_400_BAD_REQUEST
    """
    users_db = auth.get_users_db()
    user = auth.authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token_expire_minutes = int(crud_vars.getValue("ACCESS_TOKEN_EXPIRE_MINUTES"))
    access_token_expires = timedelta(minutes=access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.email, "scopes": user.scopes.split(",")},
        expires_delta=access_token_expires,
    )
    db = SessionLocal()
    db_user = users.get_user(db, user.id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado.")
    db_user_active = users.get_user_active(db, user.id)
    if not db_user_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no activo.")
    setattr(db_user, "last_login_at", datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/sign_in")
def sign_in(user: UserSignIn, db: Session = Depends(auth.get_db)):
    """
    Registrarse

    """
    db_user_same_email = users.get_user_by_email(db, email=user.email)
    if db_user_same_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya esta registrado.")
    db_user = users.sign_in(db=db, user=user)
    if db_user:
        return {"message": "Se ha realizado tu registro con éxito. Revisa tu correo para activar tu cuenta."}  
    return {"message": "Hubo un problema con el registro."}

@router.get("/activate_link/{user_id}")
def activate_link(request: Request,user_id: int,db: Session = Depends(auth.get_db)):
    """
    Activar su cuenta dando click en el enlace adjunto al correo.

    """
    try:
        token = request.query_params.get("token")
        users.activate_link(db=db,user_id=user_id,token=token)
        return {"message": "La cuenta ha sido activada."}
    except Exception as e:
        return {"message": "Hubo un error al activar la cuenta. Vuelva a intentarlo."}


@router.post("/logout")
async def logout(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    """
    Invalida el token actual de la sesión mandandolo a una lista negra.

    """
    auth.blacklist.add(token)
    return {"msg": "Se ha cerrado la sesión"}