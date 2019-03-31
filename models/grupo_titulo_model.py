from mongoengine import *
import mongoengine_goodjson as gj

class GrupoTitulo(gj.EmbeddedDocument):  
    tipo = IntField(required=True)
    nome = StringField(required=True)
