import os
import requests
import json
import random
from datetime import datetime
from database.connection import SessionLocal, engine

from schemas.Disc import SpotifyDisc, DiscCreate
from schemas.File import FileCreate
from cruds import discs
from cruds import vars as crud_vars
from models.Disc import Disc
from models.File import File as FileModel

def get_token():
    url = 'https://accounts.spotify.com/api/token'

    CLIENT_ID = crud_vars.getValue("CLIENT_ID")
    CLIENT_SECRET = crud_vars.getValue("CLIENT_SECRET")

    data = {'grant_type': 'client_credentials'}

    response = requests.post(url, auth=(CLIENT_ID, CLIENT_SECRET), data=data)

    return response.json()['access_token']


def search_spotify_api(search,limit):
    spotify_api_key = get_token()
    response = requests.get('https://api.spotify.com/v1/search?q='+search+'&type=album&limit='+str(limit), headers={'Authorization': 'Bearer ' + spotify_api_key})
    json_response = json.loads(response.text)
    albums = json_response['albums']['items']
  
    spotify_discs = [SpotifyDisc(id=album["id"], album=album["name"], artist=album["artists"][0]["name"], cover_picture=album["images"][0]["url"], year = int(album['release_date'].split("-")[0])) for album in albums]

    db = SessionLocal()
    for spotify_disc in spotify_discs:
        db_disc_same_name = discs.get_disc_by_name_and_artist(db, album=spotify_disc.album, artist=spotify_disc.artist)
        if not db_disc_same_name:
            disc = DiscCreate(album =spotify_disc.album, artist = spotify_disc.artist, genre = "spotify", year = spotify_disc.year,price = random.randint(300, 1200))
            db_disc = Disc(album = spotify_disc.album, artist = spotify_disc.artist, genre = 'spotify', year = spotify_disc.year, price = random.randint(300, 1200),created_at = datetime.now(), updated_at = datetime.now())
            for key, value in disc.dict().items():
                if value is None or value == "":
                    setattr(db_disc, key, getattr(db_disc, key))
                elif key== "created_at" or key== "updated_at" :
                    setattr(db_disc, key, datetime.now())   
                else:
                    setattr(db_disc, key, value)
            db.add(db_disc)
            db.commit()
            
            file_create = downloadAlbumCover(spotify_disc.album,spotify_disc.cover_picture)
            db_file = FileModel(file_type = file_create.file_type, file_name = file_create.file_name, file_size = file_create.file_size, file_path = file_create.file_path, file_extension = file_create.file_extension,created_at = datetime.now(), updated_at = datetime.now())
            
            if file_create:
                for key, value in file_create.dict().items():
                    if value is None or value == "":
                        setattr(db_file, key, getattr(db_file, key))
                    elif key== "created_at" or key== "updated_at" :
                        setattr(db_file, key, datetime.now())   
                    else:
                        setattr(db_file, key, value)
                db.add(db_file)
                db.commit()

            if db_file:
                setattr(db_disc, "file_id", db_file.id)
                db.add(db_disc)
                db.commit()
                db.refresh(db_disc)  
    return spotify_discs

def downloadAlbumCover(album: str, url: str, ):
    only_name = convert_to_snake_case(album)
    timestamp = datetime.now().strftime('%d_%m_%Y_%H%M%S')
    file_name = f"{only_name}_{timestamp}.png"
    
    file_location = f"upload_files/albums_covers/{file_name}"
    # Descargar la imagen desde el enlace
    response = requests.get(url)

    with open(file_location, "wb") as file_object:
        file_object.write(response.content)
    
    file_size = os.path.getsize(file_location)
    return FileCreate(file_type='albums_covers', file_name=file_name, file_size=file_size, file_path=file_location, file_extension='png')


def convert_to_snake_case(text):
    # Remover espacios en blanco al inicio y final de la cadena
    text = text.strip()
    # Reemplazar espacios en blanco con guiones bajos
    text = text.replace(" ", "_")
    # Reemplazar slash con espacios en blanco
    text = text.replace('/', '')
    # Convertir a minúsculas
    text = text.lower()
    return text