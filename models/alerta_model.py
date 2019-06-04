from mongoengine import *
import mongoengine_goodjson as gj
from models.tipo_titulo_model import TipoTitulo

class Alerta(gj.Document):
    usuario_id = StringField(required=True)
    nome_titulo = StringField(required=True)
    tipo_titulo = EmbeddedDocumentField(TipoTitulo)    
    tipo_notificacao = StringField(required=True) # "SMS" ou "EMAIL"
    situacao = IntField(required=True) # -1 menor, 0 igual ou  1 maior
    valor = DecimalField(required=True)

