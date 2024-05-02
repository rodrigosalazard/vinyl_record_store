from fastapi import Depends, HTTPException, Security, status, Request, Response, APIRouter
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from typing import  Optional
from fastapi_pagination import add_pagination, Page

from datetime import date

from schemas.Sale import SaleDiscUser
from schemas.User import User
from auth import auth
from cruds import sales as crud_sales

router = APIRouter(
    prefix="/sales",
    tags=["Venta de Discos de Vinilo"],
    responses={404: {"description": "Not found Route"}},
)

@router.get("/", response_model=Page[SaleDiscUser])
def sales(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])], page: int = 1, size: int = 2, since: Optional[date] = None,to: Optional[date] = None,db: Session = Depends(auth.get_db), search: Optional[str] = None):
    """
     Buscar discos por álbum o artista y los pagina

    """
    return crud_sales.sales(db = db,search = search, since = since,to = to)


@router.post("/download")
async def download_sales(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])], db: Session = Depends(auth.get_db), search: Optional[str] = None,since: Optional[date] = None,to: Optional[date] = None):
    """
     Descarga masivas de ventas por fecha

    """
    return crud_sales.download_sales(db, search = search, since = since, to = to)


@router.post("/report")
async def generate_sales_report(current_user: Annotated[User, Security(auth.get_current_user, scopes=["admin"])], db: Session = Depends(auth.get_db), search: Optional[str] = None,since: Optional[date] = None,to: Optional[date] = None):
    """
     Generar Reporte en PDF de ventas por mes

    """
    return crud_sales.generate_sales_report(db, search = search, since = since, to = to)