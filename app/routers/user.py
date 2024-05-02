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


from schemas.User import UserUpdate, UserDisc, UserProfile, User
from auth import auth
from cruds import users
from cruds import sales

router = APIRouter(
    prefix="/users",
    tags=["User"],
    responses={404: {"description": "Not found Route"}},
)

@router.get("/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Security(auth.get_current_user, scopes=["user"])],db: Session = Depends(auth.get_db)):
    """
    Obtiene el usuario actual de la sesión

    """
    user = users.get_user(db, user_id=current_user.id)
    return user
@router.post("/profile", response_model=User)
def update_profile(current_user: Annotated[User, Security(auth.get_current_user, scopes=["user"])],user:  UserProfile,db: Session = Depends(auth.get_db)):
    """
    Actualiza un usuario.

    """
    return users.update_profile(db=db,current_user=current_user,user=user)

@router.get("/discs/me", response_model=Page[UserDisc])
def discs_users_me(current_user: Annotated[User, Security(auth.get_current_user, scopes=["user"])], page: int = 1, size: int = 2, db: Session = Depends(auth.get_db), search: Optional[str] = None):
    """
     Buscar discos del usuario actual por álbum o artista y los pagina

    """
    return sales.user_discs(db = db, user_id = current_user.id, page=page, size=size,search = search)

def get_token(request: Request):
    """
    Esta función extrae un token del encabezado de autorización de una solicitud.
    
    :param request: El parámetro `request` es del tipo `Request`, que probablemente sea un objeto que
    representa una solicitud HTTP. Puede contener información como el método de solicitud, los
    encabezados y el cuerpo
    :type request: Request
    :return: La función `get_token` toma un objeto `Request` como entrada y devuelve una cadena de token
    si existe en el encabezado `Authorization` de la solicitud. Si el encabezado no existe o no contiene
    un token, devuelve `Ninguno`.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header:
        return auth_header.split("Bearer ")[1]
    else:
        return None