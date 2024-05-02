from fastapi import Depends, HTTPException, Security, status, Request, Response, APIRouter
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from typing import List, Union, Optional
from fastapi_pagination import add_pagination, Page


from schemas.User import User, UserCreate, UserUpdate
from auth import auth
from cruds import users

router = APIRouter(
    prefix="/users",
    tags=["Admin"],
    responses={404: {"description": "Not found Route"}},
)

#This is a function decorator that associates the function with the /users path and states that the response returned by the function must have a data model based on the list of users defined in User.
@router.get("/", response_model=List[User])
def get_users(request:Request,current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])],skip: int = 0, limit: int = 200, db: Session = Depends(auth.get_db)):
    """
     Regresa el listado de usuarios

    """
    #:param skip: Indica cuántos usuarios se deben omitir al consultar la base de datos. El valor predeterminado es 0, lo que significa que no se omitirán usuarios.
    #:type None: None
    #:optinal

    #:param limit: Indica el número máximo de usuarios que se devolverán en la respuesta. El valor predeterminado es 200.

    #:param db: Representa una sesión de base de datos proporcionada por la función auth.get_db. La sesión de base de datos se utiliza para realizar consultas a la base de datos y recuperar los usuarios que se devolverán en la respuesta.
    return users.get_users(db, skip=skip, limit=limit)


@router.get("/search", response_model=Page[User])
def get_users_paginate(request:Request,current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])],page: int = 0, size: int = 10, db: Session = Depends(auth.get_db), search: Optional[str] = None):
    """
     Buscar usuarios por nombre

    """
    return users.get_users_paginate(db, page=page, size=size, search = search)


@router.post("/", response_model=User)
def create_user(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])],user: UserCreate, db: Session = Depends(auth.get_db)):
    """
    Crea un nuevo usuario

    """
    db_user_same_email = users.get_user_by_email(db, email=user.email)
    if db_user_same_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya esta registrado.")
    return users.create_user(db=db, user=user)



@router.get("/{user_id}", response_model=User)
def get_user(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])],user_id: int, db: Session = Depends(auth.get_db)):
    """
    Obtener un usuario por ID
    :param user_id: Indica el ID del usuario a obtener
    :type user_id: Int

    :return: El usuario 
    :rtype: User

    :raises HTTPException: None HTTP_404_NOT_FOUND
    """
    db_user = users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return db_user


@router.patch("/{user_id}", response_model=User)
def update_user(token: Annotated[str, Depends(auth.oauth2_scheme)],current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])],user_id: int,user: UserUpdate,db: Session = Depends(auth.get_db)):
    """
    Actualiza el usuario.

    """
    db_user = users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    updated_user = users.update_user(db=db, user_id=user_id, user=user,current_user=current_user)
    return updated_user
    

@router.delete("/{user_id}")
def delete_user(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])],user_id: int, db: Session = Depends(auth.get_db)):
    """
    Eliminar un usuario.

    """
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No puedes eliminarte a ti mismo.")
    db_user = users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    db_user = users.delete_user(db, user_id=user_id)
    return {"message": "Usuario ha sido eliminado."} 