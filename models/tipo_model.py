from mongoengine import *
import mongoengine_goodjson as gj

class Tipo(gj.Document):  
    grupo_tipo = IntField(required=True)
    tipo = IntField(required=True)
    nome = StringField(required=True)
