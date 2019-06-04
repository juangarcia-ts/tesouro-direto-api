from mongoengine import *
import mongoengine_goodjson as gj

class Alerta(gj.Document):
    alerta_id = StringField(required=True)
    nome_titulo = StringField()
    tipo_notificacao = BooleanField()
    situacao = IntegerField() # -1 menor, 0 igual ou  1 maior
    valor = DoubleField()

