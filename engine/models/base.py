from peewee import Model
from engine.config import db

class BaseModel(Model):
    class Meta:
        database = db
