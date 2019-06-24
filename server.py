from mongoengine import *
from business.crawler_business import CrawlerBusiness
from models.alerta_model import Alerta
from models.grupo_model import Grupo
from models.tipo_model import Tipo
from models.titulo_crawler_model import TituloCrawler
from models.historico_titulos_model import HistoricoTitulos
from models.tipo_titulo_model import TipoTitulo
from models.postagem_blog_model import PostagemBlog
from models.usuario_model import Usuario
from models.titulo_pessoal_model import TituloPessoal
from flask import request, url_for
from flask_api import FlaskAPI, status
from flask_cors import CORS
from bson import json_util
import base64
import time
import os

app = FlaskAPI(__name__)
CORS(app)

# Conexão com o MongoDB (Atlas)
connect(
    'tesouro-direto',
    host=
    'mongodb+srv://admin:root@tesouro-direto-cwrre.mongodb.net/test?retryWrites=true'
)

# Controllers
## Genéricos
@app.route('/extrairdados', methods=['GET'])
def extrair_dados():
    start_time = time.time()
    httpStatus = status.HTTP_200_OK if CrawlerBusiness.excract_data(
    ) == True else status.HTTP_500_INTERNAL_SERVER_ERROR
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

    pipeline = [{
        "$unwind": '$lista_titulos'
    }, {
        "$match": {
            "lista_titulos.nome_titulo": nome,
            "lista_titulos.tipo_titulo.tipo": tipo
        }
    }, {
        "$group": {
            "_id": "$data_extracao",
            "preco": {
                "$first": "$lista_titulos.preco_unitario"
            }
        }
    }, {
        "$sort": {
            "_id": 1
        }
    }]

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

## Blog
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

    postagem = PostagemBlog(destaque=destaque,
                            titulo=titulo,
                            resumo=resumo,
                            imagem_capa=imagem_capa,
                            html=html)
    postagem.save()

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

## Usuários
@app.route('/obterusuario/<string:firebase_id>', methods=['GET'])
def obter_usuario(firebase_id):
    usuario = Usuario.objects(firebase_id=firebase_id).first()

    return usuario.to_json(), status.HTTP_200_OK

@app.route('/editarusuario', methods=['POST'])
def editar_usuario():
    firebase_id = request.data['firebase_id']
    foto = request.data['foto']
    telefone = request.data['telefone']

    usuario = Usuario.objects(firebase_id=firebase_id).first()

    if usuario:
        usuario.foto = foto
        usuario.telefone = telefone
    else:
        usuario = Usuario(firebase_id=firebase_id,
                          foto=foto,
                          telefone=telefone)

    usuario.save()

    return usuario.to_json(), status.HTTP_200_OK

## Alertas
@app.route('/obteralertas/<string:firebase_id>', methods=['GET'])
def obter_alertas(firebase_id):
    alertas = Alerta.objects(usuario_id=firebase_id).all()

    return alertas.to_json(), status.HTTP_200_OK

@app.route('/adicionaralerta', methods=['POST'])
def adicionar_alerta():
    firebase_id = request.data['firebase_id']
    nome_titulo = request.data['nome_titulo']
    tipo_notificacao = request.data['tipo_notificacao']
    situacao = request.data['situacao']
    valor = request.data['valor']
    grupo_titulo = request.data['grupo_titulo']
    tipo_titulo = request.data['tipo_titulo']

    alerta = Alerta(usuario_id=firebase_id,
                    nome_titulo=nome_titulo,
                    grupo_titulo=grupo_titulo,
                    tipo_titulo=tipo_titulo,
                    tipo_notificacao=tipo_notificacao,
                    situacao=situacao,
                    valor=valor)
    alerta.save()

    return str(alerta.id), status.HTTP_200_OK

@app.route('/removeralerta/<string:alert_id>', methods=['GET'])
def remover_alerta(alert_id):
    alerta = Alerta.objects.get(pk=alert_id)

    if alerta:
        alerta.delete()

    return "OK", status.HTTP_200_OK

@app.route('/enviaralerta', methods=['POST'])
def enviar_alerta():
    contact = request.data['contact']
    alert_id = request.data['alert_id']

    alerta = Alerta.objects.get(pk=alert_id)

    if alerta:
        alerta.send_alert(contact)

    return "OK", status.HTTP_200_OK

## Títulos Pessoais
@app.route('/titulopessoal/<string:usuario_id>/<string:titulo_id>', methods=['GET'])
def obter_titulo_pessoal(usuario_id, titulo_id):
    titulo = TituloPessoal.objects.get(pk=titulo_id)

    return titulo.to_json(), status.HTTP_200_OK

@app.route('/titulopessoal/<string:usuario_id>', methods=['GET'])
def obter_titulos_pessoais(usuario_id):
    titulos = TituloPessoal.objects(usuario_id=usuario_id).all()

    return titulos.to_json(), status.HTTP_200_OK

@app.route('/titulopessoal', methods=['POST'])
def adicionar_titulo_pessoal():
    usuario_id = request.data['usuario_id']
    descricao = request.data['descricao']
    nome_titulo = request.data['nome_titulo']
    data_aquisicao = request.data['data_aquisicao']
    valor = request.data['valor']
    taxa_rendimento = request.data['taxa_rendimento']
    observacao = request.data['observacao']

    titulo = TituloPessoal(usuario_id=usuario_id,
                           descricao=descricao,
                           nome_titulo=nome_titulo,
                           data_aquisicao=data_aquisicao,
                           valor=valor,
                           taxa_rendimento=taxa_rendimento,
                           observacao=observacao)
    titulo.save()

    return str(titulo.id), status.HTTP_200_OK

@app.route('/titulopessoal/<string:titulo_id>', methods=['PUT'])
def editar_titulo_pessoal(titulo_id):
    usuario_id = request.data['usuario_id']
    descricao = request.data['descricao']
    nome_titulo = request.data['nome_titulo']
    data_aquisicao = request.data['data_aquisicao']
    valor = request.data['valor']
    taxa_rendimento = request.data['taxa_rendimento']
    observacao = request.data['observacao']

    titulo = TituloPessoal.objects.get(pk=titulo_id)

    if titulo:
        titulo.usuario_id = usuario_id
        titulo.descricao = descricao
        titulo.nome_titulo = nome_titulo
        titulo.data_aquisicao = data_aquisicao
        titulo.valor = valor
        titulo.taxa_rendimento = taxa_rendimento
        titulo.observacao = observacao
        titulo.save()

    return str(titulo.id), status.HTTP_200_OK

@app.route('/titulopessoal/<string:titulo_id>', methods=['DELETE'])
def remover_titulo_pessoal(titulo_id):
    titulo = TituloPessoal.objects.get(pk=titulo_id)

    if titulo:
        titulo.delete()

    return "OK", status.HTTP_200_OK

# Rodar servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(debug=True)