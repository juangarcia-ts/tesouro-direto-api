from mongoengine import *
from datetime import datetime
from models.tipo_titulo_model import TipoTitulo
import mongoengine_goodjson as gj

class TituloCrawler(gj.EmbeddedDocument):    
    tipo_titulo = EmbeddedDocumentField(TipoTitulo, required=True)
    nome_titulo = StringField(required=True)
    data_vencimento = DateTimeField(required=True)
    taxa_rendimento = DecimalField(required=True)
    valor_minimo = DecimalField()
    preco_unitario = DecimalField(required=True)
    