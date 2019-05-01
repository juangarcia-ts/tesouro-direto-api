from mongoengine import *
from business.crawler_business import CrawlerBusiness
from models.grupo_model import Grupo
from models.tipo_model import Tipo
from models.titulo_crawler_model import TituloCrawler
from models.historico_titulos_model import HistoricoTitulos
from models.postagem_blog_model import PostagemBlog
from flask import request, url_for
from flask_api import FlaskAPI, status
from flask_cors import CORS
from bson import json_util
import time
import os

app = FlaskAPI(__name__)
CORS(app)

# Conexão com o MongoDB (Atlas)
connect('tesouro-direto', host='mongodb+srv://admin:root@tesouro-direto-cwrre.mongodb.net/test?retryWrites=true')

# Controllers 
@app.route('/listarpostagens', methods=['GET'])
def listar_postagens():
  postagens = PostagemBlog.objects.order_by('-data_inclusao')
  
  return postagens.to_json(), status.HTTP_200_OK

@app.route('/obterpostagem/<string:uid>', methods=['GET'])  
def obter_postagem(uid):
  postagem = PostagemBlog.objects.get(pk=uid)
  
  return postagem.to_json(), status.HTTP_200_OK  

@app.route('/adicionarpostagem', methods=['POST'])
def adicionar_postagem():
  destaque = request.data['isPostHighlight']
  titulo = request.data['postTitle']
  resumo = request.data['postSummary']
  imagem_capa = request.data['postImage']
  html = request.data['postHtml']

  postagem = PostagemBlog(destaque=destaque, titulo=titulo, resumo=resumo, imagem_capa=imagem_capa, html=html)  
  postagem.save()

  print(postagem)

  return str(postagem.id), status.HTTP_200_OK

@app.route('/editarpostagem', methods=['POST'])
def editarpostagem():
   uid = request.data['postId']
   destaque = request.data['isPostHighlight']
   titulo = request.data['postTitle']
   resumo = request.data['postSummary']
   imagem_capa = request.data['postImage']
   html = request.data['postHtml']

   postagem = PostagemBlog.objects.get(pk=uid)

   if postagem:
      postagem.destaque = destaque
      postagem.titulo = titulo
      postagem.resumo = resumo
      postagem.imagem_capa = imagem_capa
      postagem.html = html
      postagem.save()

   return str(postagem.id), status.HTTP_200_OK  

@app.route('/removerpostagem', methods=['POST'])
def remover_postagem():  
   uid = request.data['postId']

   postagem = PostagemBlog.objects.get(pk=uid)

   if postagem:
      postagem.delete()

   return "OK", status.HTTP_200_OK

@app.route('/extrairdados', methods=['GET'])
def extrair_dados():  
  start_time = time.time()
  httpStatus = status.HTTP_200_OK if CrawlerBusiness.excract_data() == True else status.HTTP_500_INTERNAL_SERVER_ERROR
  elapsed_time = time.time() - start_time

  return str(elapsed_time), httpStatus

@app.route('/listargrupos', methods=['GET'])
def listar_grupos():  
  grupos = Grupo.objects.order_by('tipo')

  return grupos.to_json(), status.HTTP_200_OK

@app.route('/listartipos', methods=['GET'])
def listar_tipos():
  tipos = Tipo.objects.order_by('tipo')

  return tipos.to_json(), status.HTTP_200_OK

@app.route('/obterhistorico', methods=['POST'])
def obter_historico():
  tipo = request.data['tipo']
  nome = request.data['nome']
  
  result = []

  pipeline = [
    { "$unwind": '$lista_titulos' },
    { "$match": { "lista_titulos.nome_titulo": nome, "lista_titulos.tipo_titulo.tipo": tipo } },
    { "$group": { "_id": "$data_extracao", "preco": { "$first": "$lista_titulos.preco_unitario" } } }, 
    { "$sort": { "_id": 1 } }   
  ]

  historico = HistoricoTitulos.objects.aggregate(*pipeline)

  for h in historico:
    result.append(h)

  if len(result) > 30:
    result = result[:30]    

  result = json_util.dumps(result)  

  return json_util.loads(result), status.HTTP_200_OK

@app.route('/obtertitulosatualizados', methods=['GET'])
def obter_titulos_atualizados():  
  titulos = HistoricoTitulos.objects.order_by('-data_extracao').first()

  return titulos.to_json(), status.HTTP_200_OK

# Rodar servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(debug=True)