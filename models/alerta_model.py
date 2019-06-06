from mongoengine import *
import mongoengine_goodjson as gj
from models.tipo_model import Tipo
from twilio.rest import Client
from urllib.parse import urlencode
import requests
import httplib2
import os
import json

with open('config.json') as config_file:
    config = json.load(config_file)

# Email (MailGun)
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY",
                                 config["mailgun"]["api_key"])
MAILGUN_DOMAIN_NAME = os.environ.get("MAILGUN_DOMAIN_NAME",
                                     config["mailgun"]["domain_name"])

# SMS (Twilio)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID",
                                    config["twilio"]["account_sid"])
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN",
                                   config["twilio"]["auth_token"])
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER",
                                     config["twilio"]["phone_number"])


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
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        situacao = ""

        message = self.obter_mensagem()

        sms = client.messages.create(body=message,
                                     from_=TWILIO_PHONE_NUMBER,
                                     to='+55{}'.format(telefone))

        print(sms.sid)
