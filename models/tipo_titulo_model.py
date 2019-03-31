from mongoengine import *
from models.grupo_titulo_model import GrupoTitulo
import mongoengine_goodjson as gj

class TipoTitulo(gj.EmbeddedDocument):  
    grupo_titulo = EmbeddedDocumentField(GrupoTitulo)
    tipo = IntField(required=True)
    nome = StringField(required=True)
