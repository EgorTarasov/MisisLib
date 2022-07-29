"""TODO: user model
username (Имя)
uni_id (номер студенческого)
TODO: Document model
id
name
folder
TODO: Folder model
id
name
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(40))
#
#     def __repl__(self):
#         return f"User(id={self.id!r}, name={self.name!r}"
#

class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    parent_id = Column(Integer, ForeignKey("folders.id"))


class Document(Base):
    __tablename__ = "docs"

    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    folder_id = Column(Integer, ForeignKey("folders.id"))
    # folder = relationship("Folder", back_populates="folders")

    def __repr__(self):
        return f"Document(id={self.id!r}, name={self.name!r}, folder={self.folder!r}"


# Initialise your models and database like so:

# from tortoise import Tortoise, run_async

# async def init():
#     # Here we create a SQLite DB using file "db.sqlite3"
#     #  also specify the app name of "models"
#     #  which contain models from "app.models"
#     await Tortoise.init(
#         db_url='sqlite://db.sqlite3',
#         modules={'models': ['app.models']}
#     )
#     # Generate the schema
#     await Tortoise.generate_schemas()

# # run_async is a helper function to run simple async Tortoise scripts.
# run_async(init())