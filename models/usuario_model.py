from mongoengine import *
import mongoengine_goodjson as gj

class Usuario(gj.Document): 
  firebase_id = StringField(required=True)
  foto = StringField()
    