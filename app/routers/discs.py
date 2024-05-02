from fastapi import Depends, HTTPException, Security, status, Request, Response, Form, File, UploadFile, APIRouter
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from datetime import datetime, timedelta, date
from typing import List, Union, Optional
from fastapi_pagination import add_pagination, Page

from schemas.User import User, UserDisc
from schemas.Disc import Disc, DiscUpdate, DiscCreate
from schemas.Sale import Sale
from auth import auth
from cruds import discs
from cruds import sales

router = APIRouter(
    prefix="/discs",
    tags=["Venta de Discos de Vinilo"],
    responses={404: {"description": "Not found Route"}},
)


@router.get("/all", response_model=List[Disc])
def get_discs(request:Request,current_user: Annotated[User, Security(auth.get_current_user, scopes=["user"])],skip: int = 0, limit: int = 200, db: Session = Depends(auth.get_db)):
    """
    Regresa el listado de discos

    """
    return discs.get_discs(db, skip=skip, limit=limit)

@router.post("/", response_model=Disc)
def create_disc(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])], db: Session = Depends(auth.get_db),
        uploaded_file: Optional[UploadFile] = None, 
        album: str = Form(...),
        artist: str = Form(...),
        genre: str = Form(...),
        year: int = Form(...),
        price: float = Form(...)):
    """
    Crea un nuevo disco con image de archivo

    """
    db_disc_same_name = discs.get_disc_by_name_and_artist(db, album=album, artist=artist)
    if db_disc_same_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El disco ya esta registrado.")
    disc = DiscCreate(album =album, artist = artist, genre = genre, year = year,price = price)
    return discs.create_disc(db = db, disc = disc, uploaded_file = uploaded_file)


@router.get("/search", response_model=Page[Disc])
def search_disc(current_user: Annotated[User, Security(auth.get_current_user, scopes=["user"])], page: int = 1, size: int = 10, db: Session = Depends(auth.get_db), search: Optional[str] = None):
    """
     Buscar discos por álbum o artista y los pagina

    """
    return discs.search_disc(db, page=page, size=size,search = search)


@router.get("/{disc_id}", response_model=Disc)
def get_disc(current_user: Annotated[User, Security(auth.get_current_user, scopes=["user"])],disc_id: int, db: Session = Depends(auth.get_db)):
    """
    Obtener un disco por ID
    """
    db_disc = discs.get_disc(db, disc_id=disc_id)
    if db_disc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disco no encontrado.")
    return db_disc


@router.delete("/{disc_id}")
def delete_disc(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])],disc_id: int, db: Session = Depends(auth.get_db)):
    """
    Eliminar un disco.

    """
    db_disc = discs.get_disc(db, disc_id=disc_id)
    if db_disc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disco no encontrado.")
    db_disc = discs.delete_disc(db, disc_id=disc_id)
    return {"message": "Disco ha sido eliminado."}   



@router.patch("/{disc_id}", response_model=Disc)
def updated_disc(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])],disc_id: int, db: Session = Depends(auth.get_db),
        uploaded_file: Optional[UploadFile] = None, 
        album: str = Form(...),
        artist: str = Form(...),
        genre: str = Form(...),
        year: int = Form(...),
        price: float = Form(...)):
    """
    Actualizar un disco 

    """
    disc = DiscUpdate(album = album, artist = artist, genre = genre, year = year,price = price)
    return discs.update_disc(db = db, disc_id = disc_id, disc = disc, uploaded_file = uploaded_file)


@router.post("/buy/{disc_id}", response_model=Sale)
def buy_disc(token: Annotated[str, Depends(auth.oauth2_scheme)],current_user: Annotated[User, Security(auth.get_current_user, scopes=["user"])],disc_id: int,db: Session = Depends(auth.get_db)):
    """
    Compra de un disco.

    """
    db_disc = discs.get_disc(db, disc_id=disc_id)
    if db_disc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disco no encontrado :(")
    return sales.buy_disc(db=db, disc_id=disc_id,current_user=current_user)





@router.get("/users/{user_id}", response_model=Page[UserDisc])
def discs_user(user_id: int, current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])], page: int = 1, size: int = 2,db: Session = Depends(auth.get_db), search: Optional[str] = None):
    """
     Buscar discos de un usuario especifico por álbum o artista y los pagina

    """
    return sales.user_discs(db = db, user_id = user_id, page=page, size=size,search = search)

@router.post("/upload")
async def upload_discs(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])],file: UploadFile = File(...), db: Session = Depends(auth.get_db)):
    """
     Carga masivas de discos mediante layout excel

    """
    return discs.upload_discs(db, uploaded_file=file)


@router.post("/download")
async def download_discs(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])], db: Session = Depends(auth.get_db), search: Optional[str] = None):
    """
     Descarga masivas de discos en excel

    """
    return discs.download_discs(db, search=search)