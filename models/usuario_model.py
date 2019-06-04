from models.alerta_model import Alerta
from mongoengine import *
import mongoengine_goodjson as gj

class Usuario(gj.Document):
  firebase_id = StringField(required=True)
  foto = StringField()
  alertas = DictField() #É para ser um dicionário 