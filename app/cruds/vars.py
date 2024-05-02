from models.Var import Var
from database.connection import SessionLocal, engine


def getValue(var_name : str):
    db = SessionLocal()
    return db.query(Var).filter(Var.name == var_name,Var.deleted_at == None).first().value