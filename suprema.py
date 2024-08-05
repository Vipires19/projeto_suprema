import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
import streamlit_authenticator as stauth
from pathlib import Path
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import urllib
import urllib.parse
from datetime import datetime

st.set_page_config(
            layout =  'wide',
            page_title = 'Suprema Sat 🌎',
        )

mongo_user = st.secrets['MONGO_USER']
mongo_pass = st.secrets["MONGO_PASS"]

username = urllib.parse.quote_plus(mongo_user)
password = urllib.parse.quote_plus(mongo_pass)
client = MongoClient("mongodb+srv://%s:%s@cluster0.gjkin5a.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" % (username, password), ssl = True)
st.cache_resource = client
db = client.supremasat
coll = db.veiculos
coll2 = db.pagamentos

def cadastrar_veiculos():
    col1,col2,col3,col4,col5,col6 = st.columns(6)
    placa_lt = col1.text_input('Placa', placeholder = 'Insira as letras da placa do veículo')
    placa_nb = col2.text_input('Placa2', placeholder = 'Insira a segunda parte da placa',label_visibility="hidden")
    modelo = col3.text_input('Modelo', placeholder = 'Insira o modelo do veículo')
    cor = col4.text_input('Cor', placeholder = 'Insira a cor do veículo')
    ano = col5.number_input('Ano',min_value= 0, max_value= 9999,value=None, placeholder = 'Insira o ano do veículo')
    tipo = col6.selectbox('Tipo', ['Carro','Moto','Caminhonete','Caminhão'])
    nome = col1.text_input('Nome do Cliente', placeholder='Insira o nome do cliente')
    tipo_doc = col2.selectbox('Tipo de documento', ['RG','CPF'])
    if tipo_doc == 'RG':
        doc = col3.text_input('Documento do cliente', placeholder='Ex: 00.000.000-0')
    if tipo_doc == 'CPF':
        doc = col3.text_input('Documento do cliente', placeholder='Ex: 000.000.000-0')
    adiciona_cliente = col1.button('Adicionar')
    placa = f'{placa_lt} - {placa_nb}'
    veiculo = {'Cliente' : nome,
               'Documento' : tipo_doc,
               'N° Doc' : doc,
               'Veículo' : modelo,
               'Placas': placa,
               'Cor' : cor,
               'Ano' : ano,
               'Tipo' : tipo}
    
    if adiciona_cliente:
        entry = [veiculo]
        result = coll.insert_many(entry)

def visualizar_veiculos():
    
    clientes = db.veiculos.find({})

    clientesdf = []
    for item in clientes:
        clientesdf.append(item)

    df = pd.DataFrame(clientesdf, columns= ['_id', 'Cliente','Documento','N° Doc', 'Veículo', 'Placas', 'Cor', 'Ano', 'Tipo'])
    df.drop(columns='_id', inplace=True)
    st.session_state['veiculos'] = df
    df = st.session_state['veiculos']
    
    st.dataframe(df)

def pagamento_veiculos():
    df = st.session_state['veiculos']
    cliente = df['Cliente'].value_counts().index
    clientes = st.selectbox('Cliente', cliente)
    df_cliente = df[df['Cliente'] == clientes]
    col1,col2,col3,col4,col5 = st.columns(5)
    doc = df_cliente['Documento'].value_counts().index[0]
    col1.metric('Documento', doc)
    num = df_cliente['N° Doc'].value_counts().index[0]
    col2.metric('num', num, label_visibility="hidden")
    tipo = df_cliente['Tipo'].value_counts().index[0]
    col3.metric('Tipo', tipo)    
    veic = df_cliente['Veículo'].value_counts().index[0]
    col4.metric('Modelo', veic)
    placa = df_cliente['Placas'].value_counts().index[0]
    col4.metric('Placa', placa)
    cor = df_cliente['Cor'].value_counts().index[0]
    col5.metric('Cor', cor)    
    ano = df_cliente['Ano'].value_counts().index[0]
    col5.metric('Ano', ano)
    forma_pgto = ['Dinheiro', 'Pix', 'Cartão Débito', 'Cartão Crédito']
    pagou = col1.selectbox('Forma de pagamento', forma_pgto)
    valor = col2.number_input('Valor', placeholder = 'Valor em R$')
    confirma_pgto = col1.button('Confirmar pagamento')
    
    if confirma_pgto:
        data = str(datetime.now().date())
        pgto = {'Cliente' : clientes,
                'Documento' : num,
                'Data' : data,
               'Forma Pagamento': pagou ,
               'Valor' : valor,
               'Status' : 'Confirmado'}
        entry = [pgto]
        result = coll2.insert_many(entry)

def visu():
    pagamentos = db.pagamentos.find({})
    pagamentosdf = []
    for item in pagamentos:
        pagamentosdf.append(item)

    dfpgto = pd.DataFrame(pagamentosdf, columns= ['_id', 'Cliente','Documento','Data', 'Forma Pagamento', 'Valor', 'Status'])
    dfpgto.drop(columns='_id', inplace=True)
    st.session_state['pagamentos'] = dfpgto
    dfpgto = st.session_state['pagamentos']
    dfveic = st.session_state['veiculos']
    df_pagamento = pd.merge(dfveic, dfpgto, on="Cliente", how='outer')
    df_pagamento.drop(columns= 'Documento_y', inplace=True)
    st.session_state['df_pagamento'] = df_pagamento
    df = st.session_state['df_pagamento']
    st.dataframe(df)

def pagina_principal():
    st.title('Suprema Sat 🌎')
    cadastrar_veiculos()
    visualizar_veiculos()
    
    st.divider()

    st.header('**Pagamento**')
    pagamento_veiculos()

    st.divider()
    st.header('**Visulizando pagamentos**')
    visu()

def main():
    pagina_principal()

if __name__ == '__main__':
    main()