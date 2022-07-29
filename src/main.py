import uvicorn
import requests
from fastapi import FastAPI
from schemas import FolderSchema, DocumentSchema, UserSchema
from sqlalchemy import create_engine
from models import Base


app = FastAPI()

engine = create_engine("sqlite://", echo=True, future=True)
Base.metadata.create_all(engine)


@app.get("/folder/{folder_id}")
async def get_folder(folder_id: int):
    s = requests.Session()
    u = UserSchema()
    u.login(s)
    f = FolderSchema(folder_id, s)
    return f.json()


@app.get("/documents/{document_id}")
async def get_document(document_id: int):
    s = requests.Session()
    u = UserSchema()
    u.login(s)
    d = DocumentSchema(document_id, "name")
    return d.get_url()


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, use_colors=True)