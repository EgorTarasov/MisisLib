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


from tortoise.models import Model
from tortoise import fields

class User(Model):
    id: fields.IntField(pk=True)
    name = fields.TextField()


class Folder(Model):
    id: fields.IntField(pk=True)
    name: fields.TextField()


class Document(Model): 
    id: fields.IntField(pk=True)
    name: fields.TextField()
    folder: fields.ForeignKeyField(Folder, related_name="Folder")


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