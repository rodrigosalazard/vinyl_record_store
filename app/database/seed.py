from fastapi import Depends, FastAPI, HTTPException, Security, status, Request, Response
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from sqlalchemy import inspect, event
from sqlalchemy.orm import Session

from typing_extensions import Annotated
from datetime import datetime, timedelta
from typing import List, Union, Optional
from fastapi_pagination import add_pagination, Page

from database.connection import SessionLocal, engine
from models import Disc, File, Sale, User, Var
import schemas
import auth 



# This method receives a connection, inserts one user data on database after its create.
def seed_users(connection):
    user_seed =  User.User(
        name='Admin',
        username='admin',
        email='admin@admin.com',
        password='$2b$12$GKn0bEgGe5drNu0Wf4FgP.377FSBugHAMYST/iTOHyL8Vdp/Dq9l6', #password:pass
        scopes='admin,user',
        disabled=0,
        created_at=datetime.now(),
        updated_at=datetime.now()
        )     
    connection.add(user_seed)
    connection.commit()
    connection.refresh(user_seed)
    return user_seed

# This method receives a connection, inserts one var data on database after its create.
def seed_vars(connection):
    var_seed_secret_key =  Var.Var(
        name='SECRET_KEY',
        value='9f0c089cc405abfbe78673a6627456e5ab1553b4253408277a2c9f1304e7158f',
        description ="ALGORITHM HS256",
        created_at=datetime.now(),
        updated_at=datetime.now()
        )     
    connection.add(var_seed_secret_key)
    connection.commit()
    connection.refresh(var_seed_secret_key)

    var_seed_algorithm =  Var.Var(
        name='ALGORITHM',
        value="HS256",
        description ="ENCRYPTION ALGORITHM",
        created_at=datetime.now(),
        updated_at=datetime.now()
        )     
    connection.add(var_seed_algorithm)
    connection.commit()
    connection.refresh(var_seed_algorithm)

    var_seed_access_token_expire_minutes =  Var.Var(
        name='ACCESS_TOKEN_EXPIRE_MINUTES',
        value=30,
        description ="TOKEN EXPIRATION TIME",
        created_at=datetime.now(),
        updated_at=datetime.now()
        )     
    connection.add(var_seed_access_token_expire_minutes)
    connection.commit()
    connection.refresh(var_seed_access_token_expire_minutes)

    var_seed_client_id_spotify =  Var.Var(
        name='CLIENT_ID',
        value='ef7fd1d24b3040569e6026e459994331',
        description ="CLIENT ID SPOTIFY",
        created_at=datetime.now(),
        updated_at=datetime.now()
        )     
    connection.add(var_seed_client_id_spotify)
    connection.commit()
    connection.refresh(var_seed_client_id_spotify)

    var_seed_client_secret_spotify =  Var.Var(
        name='CLIENT_SECRET',
        value='3e5c3506f0b54f1d8df2513543c094b3',
        description ="CLIENT SECRET SPOTIFY",
        created_at=datetime.now(),
        updated_at=datetime.now()
        )     
    connection.add(var_seed_client_secret_spotify)
    connection.commit()
    connection.refresh(var_seed_client_secret_spotify)

    return var_seed_client_secret_spotify 



# This method create all table to databasen, check if tables already exists and inserts data on database after its create
def initialize_data_base():

    if not inspect(engine).has_table('vars'):
        Var.Base.metadata.tables['vars'].create(engine)  
        event.listen(Var.Var.__table__,'after_create', seed_vars(connection=SessionLocal()))

    if not inspect(engine).has_table('users'):
        User.Base.metadata.tables['users'].create(engine)  
        event.listen(User.User.__table__,'after_create', seed_users(connection=SessionLocal()))

    if not inspect(engine).has_table('files') : File.Base.metadata.tables['files'].create(engine)
    if not inspect(engine).has_table('discs') : Disc.Base.metadata.tables['discs'].create(engine)
    if not inspect(engine).has_table('sales') : Sale.Base.metadata.tables['sales'].create(engine)

    Disc.Base.metadata.create_all(bind=engine)
    File.Base.metadata.create_all(bind=engine)
    Sale.Base.metadata.create_all(bind=engine)
    User.Base.metadata.create_all(bind=engine)
    Var.Base.metadata.create_all(bind=engine)