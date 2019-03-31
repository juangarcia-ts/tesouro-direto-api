from mongoengine import *
from business.crawler_business import CrawlerBusiness
from models.grupo_titulo_model import GrupoTitulo
from models.tipo_titulo_model import TipoTitulo
from models.titulo_crawler_model import TituloCrawler
from models.historico_titulos_model import HistoricoTitulos
from flask_api import FlaskAPI
from flask_api import status
from flask_cors import CORS
import time
import os

app = FlaskAPI(__name__)
CORS(app)

# Conexão com o MongoDB (Atlas)
connect('tesouro-direto', host='mongodb+srv://admin:root@tesouro-direto-cwrre.mongodb.net/test?retryWrites=true')

# Controllers 
@app.route('/extrairdados', methods=['GET'])
def extrair_dados():  
  start_time = time.time()
  httpStatus = status.HTTP_200_OK if CrawlerBusiness.excract_data() == True else status.HTTP_500_INTERNAL_SERVER_ERROR
  elapsed_time = time.time() - start_time

  return str(elapsed_time), httpStatus

@app.route('/obtertitulosatualizados', methods=['GET'])
def obter_titulos_atualizados():  
  historico = HistoricoTitulos.objects.order_by('-data_extracao').first()
  
  try:
      historico = HistoricoTitulos.objects.order_by('-id').first()
      httpStatus = status.HTTP_200_OK
  except:
      httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR

  return historico.to_json(), httpStatus

# Rodar servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)