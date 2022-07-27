import uvicorn
import requests
from fastapi import FastAPI
from schemas import FolderSchema, DocumentSchema, UserSchema


app = FastAPI()


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
    return d.json()


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, use_colors=True)