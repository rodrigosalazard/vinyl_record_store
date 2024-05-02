import os
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import File, UploadFile
from schemas.File import FileCreate
from models.File import File as FileModel


def uploadFile(type_file:str, file: UploadFile = File(...)):
    timestamp = datetime.now().strftime('%d_%m_%Y_%H%M%S')
    only_name = file.filename.split(".")[0]
    file_extension = file.filename.split(".")[-1]
    file_name = f"{only_name}_{timestamp}.{file_extension}"
    file_location = f"upload_files/{type_file}/{file_name}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    file_size = os.path.getsize(file_location)
    return FileCreate(file_type = type_file, file_name = file_name, file_size =file_size , file_path = file_location , file_extension =file_extension)


def delete_file(db: Session, file_id: int):
    """
    Elimina un usuario, valida que exista y guarda fecha y hora de elminación.
    """
    db_file = db.query(FileModel).filter_by(id=file_id).first()
    if db_file:
        setattr(db_file, 'deleted_at', datetime.now())     
        db.commit()
        db.refresh(db_file)
