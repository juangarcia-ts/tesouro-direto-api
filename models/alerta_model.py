from mongoengine import *
import mongoengine_goodjson as gj
from models.tipo_model import Tipo
from twilio.rest import Client
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class Alerta(gj.Document):
    usuario_id = StringField(required=True)
    nome_titulo = StringField(required=True)
    grupo_titulo = IntField(required=True)
    tipo_titulo = IntField(required=True)
    tipo_notificacao = StringField(required=True) # "SMS" ou "EMAIL"
    situacao = IntField(required=True) # -1 menor, 0 igual ou  1 maior
    valor = DecimalField(required=True)
    enviado = BooleanField(required=True, default=False)

    def send_alert(self, contatc):
        if tipo_notificacao:
            alerta_smtp(contatc, nome_titulo)
        else:
            alerta_sms(contatc, nome_titulo)

    def alerta_smtp(email, titulo):
        message = Mail(
            from_email='augusto.assuncao@uniriotec.br',
            to_emails= email,
            subject= 'O seu alerta foi disparado',
            html_content= '<strong>Seu alerta do titulo: {} foi acionado hoje.</strong>'.format(titulo)
        )
        try:
            sg = SendGridAPIClient(os.environ.get('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'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)

    def alerta_sms(telefone, nome_titulo):
        account_sid = 'ACe11d51b65ee49ae0e5e20ee91255fff5'
        auth_token = '9f2e1271e7d4b41f10dac1c9d5e4a434'
        client = Client(account_sid, auth_token)

        message = client.messages \
                    .create(
                        body="Seu alerta para o titulo: {} foi disparado!".format(nome_titulo),
                        from_='+18282374201',
                        to='+55{}'.format(telefone)
                    )

        print(message.sid)