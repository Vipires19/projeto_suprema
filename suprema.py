import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
import streamlit_authenticator as stauth
from pathlib import Path

st.set_page_config(
            layout =  'wide',
            page_title = 'Suprema Sat 🌎',
        )

def cadastrar_veiculos():
    col1,col2,col3,col4,col5,col6 = st.columns(6)
    placa_lt = col1.text_input('Placa', placeholder = 'Insira as letras da placa do veículo')
    placa_nb = col2.number_input('',min_value= 0, max_value= 9999, value=None, placeholder = 'Insira os numeros da placa')
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
    adiciona_produto = col6.button('Adicionar')
    placa = f'{placa_lt} - {placa_nb}'
    veiculo = [placa,modelo,cor,ano,tipo]
    veiculo

def pagina_principal():
    st.title('Suprema Sat 🌎')
    cadastrar_veiculos()

def main():
    pagina_principal()

if __name__ == '__main__':
    main()