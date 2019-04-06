from mongoengine import *
import mongoengine_goodjson as gj

class Grupo(gj.Document):  
    tipo = IntField(required=True)
    nome = StringField(required=True)