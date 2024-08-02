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

def cadastrar_veiculos():
    col1,col2,col3,col4,col5,col6 = st.columns(6)
    placa_lt = col1.text_input('Placa', placeholder = 'Insira as letras da placa do veículo')
    placa_nb = col2.text_input('', placeholder = 'Insira a segunda parte da placa')
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

def pagina_principal():
    st.title('Suprema Sat 🌎')
    cadastrar_veiculos()
    clientes = db.veiculos.find({})

    clientesdf = []
    for item in clientes:
        clientesdf.append(item)

    df = pd.DataFrame(clientesdf, columns= ['_id', 'Cliente','Documento','N° Doc', 'Veículo', 'Placas', 'Cor', 'Ano', 'Tipo'])
    df.drop(columns='_id', inplace=True)
    st.dataframe(df)

def main():
    pagina_principal()

if __name__ == '__main__':
    main()