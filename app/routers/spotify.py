from fastapi import Depends, Request, Security,Response, APIRouter
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from typing import Optional
from schemas.User import User
from auth import auth
from cruds import discs

router = APIRouter(
    prefix="/spotify",
    tags=["Spotify"],
    responses={404: {"description": "Not found Route"}},
)


@router.get("/search/{search}")
def spotify_search_disc(current_user: Annotated[User, Security(auth.get_current_user, scopes=["user"])], size: int = 10, db: Session = Depends(auth.get_db), search: Optional[str] = None):
    """
     Buscar discos por álbum o artista en la API de Spotify

    """
    return discs.spotify_search_disc(db,size=size,search = search)