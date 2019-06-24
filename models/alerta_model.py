from mongoengine import *
import mongoengine_goodjson as gj
from models.tipo_model import Tipo
from urllib.parse import urlencode
import requests
import httplib2
import os
import json
import nexmo

config = dict()

# if (os.environ["HEROKU"] != "TRUE"):
#     with open('config.json') as config_file:
#         config = json.load(config_file)

#     MAILGUN_API_KEY = config["mailgun"]["api_key"]
#     MAILGUN_DOMAIN_NAME = config["mailgun"]["domain_name"]
#     NEXMO_API_KEY = config["nexmo"]["api_key"]
#     NEXMO_API_SECRET = config["nexmo"]["api_secret"]

# else:
#     MAILGUN_API_KEY = os.environ["MAILGUN_API_KEY"]
#     MAILGUN_DOMAIN_NAME = os.environ["MAILGUN_DOMAIN_NAME"]
#     NEXMO_API_KEY = os.environ["NEXMO_API_KEY"]
#     NEXMO_API_SECRET = os.environ["NEXMO_API_SECRET"]

class Alerta(gj.Document):
    usuario_id = StringField(required=True)
    nome_titulo = StringField(required=True)
    grupo_titulo = IntField(required=True)
    tipo_titulo = IntField(required=True)
    tipo_notificacao = StringField(required=True)  # "SMS" ou "EMAIL"
    situacao = IntField(required=True)  # -1 menor, 0 igual ou  1 maior
    valor = DecimalField(required=True)
    enviado = BooleanField(required=True, default=False)

    def obter_mensagem(self):
        if (self.situacao == -1):
            situacao = "está abaixo de"
        elif (self.situacao == 1):
            situacao = "está acima de"
        else:
            situacao = "alcançou"

        return "Seu alerta para o titulo {} foi disparado! O valor {} R$ {}".format(
            self.nome_titulo, situacao, self.valor)

    def send_alert(self, contact):
        if self.tipo_notificacao == "EMAIL":
            self.alerta_smtp(contact)
        else:
            self.alerta_sms(contact)

    def alerta_smtp(self, email):
        http = httplib2.Http()
        http.add_credentials('api', MAILGUN_API_KEY)

        message = self.obter_mensagem()

        url = 'https://api.mailgun.net/v3/{}/messages'.format(
            MAILGUN_DOMAIN_NAME)

        data = {
            'from': 'Meu Tesouro <mailgun@{}>'.format(MAILGUN_DOMAIN_NAME),
            'to': email,
            'subject': '[Meu Tesouro] Um alerta foi disparado',
            'text': message
        }

        resp, content = http.request(
            url,
            'POST',
            urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"})

        if resp.status != 200:
            raise RuntimeError('Mailgun API error: {} {}'.format(
                resp.status, content))

    def alerta_sms(self, telefone):
        message = self.obter_mensagem()

        client = nexmo.Client(key=NEXMO_API_KEY, secret=NEXMO_API_SECRET)

        client.send_message({
            'from': 'Nexmo',
            'to': '55{}'.format(telefone),
            'text': message,
        })
        
