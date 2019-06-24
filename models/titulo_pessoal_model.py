from mongoengine import *
import mongoengine_goodjson as gj

class TituloPessoal(gj.Document):  
    usuario_id = StringField(required=True)
    descricao = StringField(required=True)
    nome_titulo = StringField(required=True)
    data_aquisicao = DateTimeField(required=True)
    valor = DecimalField(required=True)
    taxa_rendimento = DecimalField(required=True)
    observacao = StringField()

