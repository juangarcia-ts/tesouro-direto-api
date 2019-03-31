from mongoengine import *
from models.grupo_titulo_model import GrupoTitulo
from models.tipo_titulo_model import TipoTitulo
from models.titulo_crawler_model import TituloCrawler
from models.historico_titulos_model import HistoricoTitulos
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json
import re

class CrawlerBusiness:
    def excract_data():
        # Requisição para o site do Ministério da Fazenda
        page = requests.get('http://www.tesouro.fazenda.gov.br/tesouro-direto-precos-e-taxas-dos-titulos')

        # Parse do HTML através do BeautifulSoup
        html = BeautifulSoup(page.text, 'html.parser')        

        # Verifica se os dados estão atualizados
        try:
            # Data da última atualização
            data_ultima_atualizacao = html.find(class_='sanfonado').next_sibling.next_sibling.next_sibling.next_sibling.text
            data_ultima_atualizacao = datetime.strptime(data_ultima_atualizacao, '%d/%m/%Y %H:%M')

            # Data da última extração
            ultimo_registro = HistoricoTitulos.objects.order_by('-id').first()
            data_ultima_extracao = ultimo_registro.data_extracao

            # Caso haja, verifica se o último adicionado está desatualizado em relação ao site da Fazenda
            if (data_ultima_extracao >= data_ultima_atualizacao):
                print("Dados atualizados. Abortando...")
                return True
        except:
            print("Iniciando extração...")

        # Pegar as duas tabelas (Investir e Resgatar)
        tables = html.find_all(class_='tabelaPrecoseTaxas')        

        #Variáveis
        historico_titulos = HistoricoTitulos()    
        historico_titulos.lista_titulos = [] 
        table_index = 1
        row_index = 1

        #Para cada tabela, buscar todas as linhas
        for table in tables:    
            # Identificar qual o grupo de títulos (1: 'Investimento', 2: 'Resgate')           :
            nome_grupo = 'Investimento' if table_index == 1 else 'Resgate'
            grupo_titulo = GrupoTitulo(nome=nome_grupo, tipo=table_index)         

            # Procurar todos as rows da tabela
            rows = table.find_all('tr')
            
            #Remover a linha do titulo principal da tabela
            rows = list(filter(lambda x: x.get('class') == None or x.get('class')[0] != 'tabelaTitulo', rows))            
                  
            tipo_titulo = TipoTitulo()                    
            # Para cada linha, buscar suas células com os valores
            for row in rows:                
                novo_titulo = TituloCrawler()

                data = row.find_all(class_=['listing0', 'listing'])                   

                # Caso a busca não retorne nada, a célula é título da seção (Ex: Indexados ao IPCA, Prefixados, etc...)
                if (len(data) == 0):
                  header = row.find_all(class_='tittuloTabelaTesouroDireto')
                  header = header[0].text.rstrip()

                  # Obter tipo do título
                  tipo_titulo = TipoTitulo(grupo_titulo=grupo_titulo, nome=header, tipo=row_index)                    
                                    
                  row_index += 1                  
                else:   
                  index = 0  

                  # Criar um objeto com as propriedades
                  for d in data:                     
                      content = CrawlerBusiness.format_value(d.text)
                      
                      if (index == 0):
                        novo_titulo.nome_titulo = content
                      elif (index == 1):
                        novo_titulo.data_vencimento = content
                      elif (index == 2):
                        novo_titulo.taxa_rendimento = float(content)
                      # O campo "Valor Mínimo" existe somente no primeiro grupo ('Investimento')
                      elif (index == 3 and table_index == 1):
                        novo_titulo.valor_minimo = float(content)
                      else:
                        novo_titulo.preco_unitario = float(content)

                      index += 1

                  novo_titulo.tipo_titulo = tipo_titulo
                  historico_titulos.lista_titulos.append(novo_titulo) 
                  historico_titulos = historico_titulos.save()

            table_index += 1 

        print("Extraído com sucesso")
        return True

    # Remove todos os caracteres inválidos dos números           
    def format_value(value):
        newValue = value.strip()
        return newValue.replace('.','').replace(',','.').replace('R$','')
