from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import or_
from passlib.hash import bcrypt
from datetime import datetime

from fastapi import HTTPException, status
from typing import List, Union, Optional
from email_validator import validate_email, EmailNotValidError

from schemas.User import UserSignIn, UserCreate, UserUpdate, UserProfile
from schemas import User as UserSchema
from models.User import User
from fastapi_pagination import paginate
from emails import settings
import secrets

def sign_in(db: Session, user: UserSignIn):
    """
    Crea un nuevo usuario, valida su correo y confirma su contraseña, guarda fecha y hora de creación.
    """
    # Generar token aleatorio
    

    if user.email: check_email(user.email)
    check_password(user.password,user.confirm_password)
    db_user = User(name = user.name,email=user.email,username=user.username, disabled =1,created_at=datetime.now(),updated_at=datetime.now(),scopes="user")
    for key, value in user.dict(exclude={"confirm_password"}).items():
        if key == "password" and value is not None and value != "":
            value = bcrypt.hash(value)
            setattr(db_user, key, value)
        elif value is None or value == "":
            setattr(db_user, key, getattr(db_user, key))
        elif key== "created_at" or key== "updated_at" :
            setattr(db_user, key, datetime.now())   
        else:
            setattr(db_user, key, value)

    token = secrets.token_urlsafe()
    setattr(db_user, "remember_token", token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Construir enlace de activación
    enlace_activacion = f'http://localhost:8000/activate_link/{db_user.id}?token={token}'
    try:
        # email_config.send_email(user, enlace_activacion)
        settings.send_email(user, enlace_activacion)
    except Exception as e:
        db.rollback()
        print("Error al enviar el correo:", str(e))

    return db_user

def activate_link(db: Session, user_id: int, token: str):
    db_user = db.query(User).filter(User.id == user_id,User.remember_token == token).first()
    if db_user:
        setattr(db_user, 'updated_at', datetime.now())     
        setattr(db_user, 'disabled',0)     
        db.commit() 
        db.refresh(db_user)
    else:
        raise HTTPException(detail="La cuenta no ha sido encontrada.",status_code=status.HTTP_400_BAD_REQUEST)

def get_user(db: Session, user_id: int):
    """
    Función busca un usuario en la base de datos, siempre y cuando dicho usuario no haya sido eliminado. Si lo encuentra, devuelve ese usuario; de lo contrario, devuelve None.

    :param db: Conexión a la base de datos
    :type db: Session
    :param user_id: Identificador de usuario.
    :type user_id: Int

    :return: Usuario de la base de datos
    :rtype: User

    """
    return db.query(User).filter(User.id == user_id,User.deleted_at == None).first()

def get_user_active(db: Session, user_id: int):
    """
    Función busca un usuario en la base de datos, siempre y cuando dicho usuario no haya sido eliminado. Si lo encuentra, devuelve ese usuario; de lo contrario, devuelve None.

    :param db: Conexión a la base de datos
    :type db: Session
    :param user_id: Identificador de usuario.
    :type user_id: Int

    :return: Usuario de la base de datos
    :rtype: User

    """
    return db.query(User).filter(User.id == user_id,User.deleted_at == None,User.disabled == 0).first()



def get_user_by_email(db: Session, email: str):
    """
    Función busca un usuario en la base de datos por el campo email.
    """
    return db.query(User).filter(User.email == email,User.deleted_at == None).first()


def get_users(db: Session, skip: int = 0, limit: int = 200):
    """
    Regresa el listado de los usuarios de la base de datos.
    """
    return db.query(User).filter(User.deleted_at == None).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    """
    Crea un nuevo usuario, valida su correo y confirma su contraseña, guarda fecha y hora de creación.
    """
    if user.email: check_email(user.email)
    check_password(user.password,user.confirm_password)
    db_user = User(name = user.name,email=user.email,username=user.username, disabled =0,created_at=datetime.now(),updated_at=datetime.now(),scopes=user.scopes)
    for key, value in user.dict(exclude={"confirm_password"}).items():
        if key == "password" and value is not None and value != "":
            value = bcrypt.hash(value)
            setattr(db_user, key, value)
        elif value is None or value == "":
            setattr(db_user, key, getattr(db_user, key))
        elif key== "created_at" or key== "updated_at" :
            setattr(db_user, key, datetime.now())   
        else:
            setattr(db_user, key, value)


    token = secrets.token_urlsafe()
    setattr(db_user, "remember_token", token)
    setattr(db_user, "disabled", 1)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    
    # Construir enlace de activación
    enlace_activacion = f'http://localhost:8000/activate_link/{db_user.id}?token={token}'
    # email_config.send_email(user, enlace_activacion)
    settings.send_email(user, enlace_activacion)

    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate,current_user:UserSchema):
    """
    Actualiza los campos del usuario , valida que su correo no cambie porque sino cierra sesión y confirma su contraseña, guarda fecha y hora de actualización.
    """
    if user.email: check_email(user.email)
    check_password(user.password,user.confirm_password)
    if user_id == current_user.id and user.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No puede editar su propio correo electrónico."
        )
    
    db_user = db.query(User).filter(User.id == user_id, User.deleted_at == None).first()
    for key, value in user.dict(exclude={"confirm_password"}).items():
        if key == "password" and value is not None and value != "":
            value = bcrypt.hash(value)
            setattr(db_user, key, value)
        elif value is None or value == "":
            setattr(db_user, key, getattr(db_user, key))
        else:
            setattr(db_user, key, value)
    setattr(db_user, 'updated_at', datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_profile(db: Session, current_user: UserSchema, user: UserProfile):
    """
    Actualiza los campos del usuario actual , valida que su correo no cambie porque sino cierra sesión y confirma su contraseña, guarda fecha y hora de actualización.
    """
    check_password(user.password,user.confirm_password)
    db_user = db.query(User).filter(User.id == current_user.id, User.deleted_at == None).first()
    for key, value in user.dict().items():
        if key == "password" and value is not None:
            value = bcrypt.hash(value)
            setattr(db_user, key, value)
        elif value is None or value == "":
            setattr(db_user, key, getattr(db_user, key))
        else:
            setattr(db_user, key, value)
    setattr(db_user, 'updated_at', datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    """
    Elimina un usuario, valida que exista y guarda fecha y hora de elminación.
    """
    db_user = db.query(User).filter_by(id=user_id).first()
    setattr(db_user, 'deleted_at', datetime.now())     
    db.commit()
    db.refresh(db_user)


def check_email(email: str):
    """
    Valida el email. 
    """
    try:
        validation = validate_email(email, check_deliverability=False)
        return validation.email
    except EmailNotValidError as e:
        raise HTTPException(detail=f"'{email}' no es un correo válido.",
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

def check_password(password:str,confirm_password:str):
    """
    Valida que la contraseña sea confirmada dos veces.
    """
    if password and confirm_password and password != confirm_password: 
        raise HTTPException(detail="Las contraseñas no coinciden.",status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if (password is not None) and (confirm_password is None or confirm_password == ""):
        raise HTTPException(detail="Falta confirmación de contraseña.",status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


    
def get_users_paginate(db: Session, page: int = 0, size: int = 10, search: Optional[str] = None):
    """
    Buscar discos por álbum o artista
    """
    # return db.query(models.Disc).filter(
    #     models.Disc.deleted_at == None,
    #     or_(models.Disc.album.ilike(f"%{search}%"), models.Disc.artist.ilike(f"%{search}%"))).offset(skip).limit(limit).all()
    query = db.query(User).filter(User.deleted_at == None)
    if search:
        query = query.filter(
            or_(User.name.ilike(f"%{search}%"), User.username.ilike(f"%{search}%"))
        )
    total = query.count()
    results = query.all()
    # Crear el diccionario de respuesta
    return paginate(results)