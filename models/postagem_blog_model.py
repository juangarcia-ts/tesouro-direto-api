from mongoengine import *
from mongoengine import signals
from datetime import datetime
import mongoengine_goodjson as gj

class PostagemBlog(gj.Document):  
    destaque = BooleanField(required=True)
    titulo = StringField(required=True)
    resumo = StringField(required=True)
    data_inclusao = DateTimeField()   
    imagem_capa = StringField(required=True)
    html = StringField(required=True)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.data_inclusao = datetime.now()

signals.pre_save.connect(PostagemBlog.pre_save, sender=PostagemBlog)