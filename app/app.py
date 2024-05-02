from fastapi import Depends, FastAPI, APIRouter
from typing_extensions import Annotated
from fastapi_pagination import add_pagination

from schemas.User import User
from auth import auth
from database import seed 

from routers import auth as auth_routes
from routers import admin, user, discs, sales, spotify

# This method initialize database connection and create all tables and seeds
seed.initialize_data_base()

app = FastAPI() 

#This function decorator used to associate a function with a specific HTTP path. In this case, the path is the server's root path, represented by the forward slash /.
@app.get("/", tags=["Hello World"])
async def hello_world():
    """
    This route just say Hi!
    """
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup():
    """
    Esta función se ejecuta cuando la aplicación se inicia y carga la información de autenticación del
    usuario.
    This function decorator used to indicate that the decorated function should be executed automatically when the application starts.
    """
    auth.load_users()

@app.get("/status/",tags=["Estatus"])
async def read_system_status(current_user: Annotated[User, Depends(auth.get_current_user)]):
    """
    Esta función recupera el estado de la sesión del usuario actual.
    
    :param current_user: Un parámetro anotado de tipo `User` que se obtiene utilizando la
    dependencia `auth.get_current_user`. Este parámetro representa al usuario actual que realiza la
    solicitud y se utiliza para garantizar que solo los usuarios autenticados puedan acceder a este
    punto final
    :type current_user: Annotated[User, Depends(auth.get_current_user)]
    :return: Se devuelve un diccionario con una clave "estado" y un valor "ok".
    """
    return {"status": "ok"}

app.include_router(auth_routes.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(discs.router)
app.include_router(sales.router)
app.include_router(spotify.router)


add_pagination(app)

