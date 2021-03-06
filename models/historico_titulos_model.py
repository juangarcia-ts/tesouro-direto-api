from mongoengine import *
from mongoengine import signals
from datetime import datetime
import mongoengine_goodjson as gj
from models.titulo_crawler_model import TituloCrawler

class HistoricoTitulos(gj.Document):    
    data_extracao = DateTimeField()    
    lista_titulos = ListField(EmbeddedDocumentField(TituloCrawler))

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.data_extracao = datetime.now()

signals.pre_save.connect(HistoricoTitulos.pre_save, sender=HistoricoTitulos)

