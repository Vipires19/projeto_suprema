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

file_path = Path(__file__).parent/"db"/"hashed_pw.pkl"

with file_path.open("rb") as file:
  hashed_passwords = pickle.load(file)
  
credentials = {
    "usernames": {
        "admin": {
            "name": "Admin",
            "password": hashed_passwords[0]
        }
    }
}

authenticator = stauth.Authenticate(credentials= credentials, cookie_name="st_session", cookie_key="key123", cookie_expiry_days= 1)
authenticator.login()

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
        doc1 = col3.text_input('Documento do cliente', placeholder='Ex: 00')
        doc2 = col4.text_input('1', placeholder='Ex: 000',label_visibility= 'hidden')
        doc3 = col5.text_input('2', placeholder='Ex: 000',label_visibility= 'hidden')
        doc4 = col6.text_input('3', placeholder='Ex: 0',label_visibility= 'hidden')
        doc = f'{doc1}.{doc2}.{doc3}-{doc4}'
    if tipo_doc == 'CPF':
        doc1 = col3.text_input('Documento do cliente', placeholder='Ex: 000')
        doc2 = col4.text_input('1', placeholder='Ex: 000',label_visibility= 'hidden')
        doc3 = col5.text_input('2', placeholder='Ex: 000',label_visibility= 'hidden')
        doc4 = col6.text_input('3', placeholder='Ex: 00',label_visibility= 'hidden')
        doc = f'{doc1}.{doc2}.{doc3}-{doc4}'
    tele = col1.text_input('DDD', placeholder='Ex: 16')
    fo = col2.text_input('Telefone', placeholder= 'Ex: 99999')
    ne = col3.text_input('fone', placeholder= 'Ex: 0000', label_visibility='hidden')
    telefone = f'({tele}){fo}-{ne}'
        
    adiciona_cliente = col1.button('Adicionar')
    placa = f'{placa_lt} - {placa_nb}'
    veiculo = {'Cliente' : nome,
               'Documento' : tipo_doc,
               'N° Doc' : doc,
               'Veículo' : modelo,
               'Placas': placa,
               'Cor' : cor,
               'Ano' : ano,
               'Tipo' : tipo,
               'Telefone' : telefone}
    
    if adiciona_cliente:
        entry = [veiculo]
        result = coll.insert_many(entry)

def visualizar_veiculos():
    
    clientes = db.veiculos.find({})

    clientesdf = []
    for item in clientes:
        clientesdf.append(item)

    df = pd.DataFrame(clientesdf, columns= ['_id', 'Cliente','Documento','N° Doc', 'Veículo', 'Placas', 'Cor', 'Ano', 'Tipo', 'Telefone'])
    df.drop(columns='_id', inplace=True)
    st.session_state['veiculos'] = df
    #    df = st.session_state['veiculos']
    #    
    #    st.dataframe(df)
    #    veiculos_cadastrados = df['Placas'].value_counts().sum()
    #    st.session_state['veiculos_cadastrados'] = veiculos_cadastrados
    #    clientes_cadastrados = df['Cliente'].nunique()
    #    st.session_state['clientes_cadastrados'] = clientes_cadastrados

def pagamento_veiculos():
    df = st.session_state['veiculos']
    placa = df['Placas'].value_counts().index
    placas = st.selectbox('Placa', placa)
    df_cliente = df[df['Placas'] == placas]
    col1,col2,col3,col4,col5 = st.columns(5)
    veiculo = df_cliente['Veículo'].value_counts().index[0]
    col1.metric('Veículo', veiculo)
    cor = df_cliente['Cor'].value_counts().index[0]
    col2.metric('Cor', cor)
    cliente = df_cliente['Cliente'].value_counts().index[0]
    col3.metric('Cliente', cliente)
    doc = df_cliente['Documento'].value_counts().index[0]
    col4.metric('Documento', doc)
    num = df_cliente['N° Doc'].value_counts().index[0]
    col5.metric('num', num, label_visibility="hidden")
    ano = df_cliente['Ano'].value_counts().index[0]
    col1.metric('Ano', ano)
    tipo = df_cliente['Tipo'].value_counts().index[0]
    col2.metric('Tipo', tipo)
    col3.metric('Tel', df_cliente['Telefone'].value_counts().index[0])    
    forma_pgto = ['Dinheiro', 'Pix', 'Cartão Débito', 'Cartão Crédito']
    pagou = col4.selectbox('Forma de pagamento', forma_pgto)
    valor = col5.number_input('Valor', placeholder = 'Valor em R$')
    confirma_pgto = col4.button('Confirmar pagamento')

    if confirma_pgto:
        dias = datetime.now().date()
        dia = dias.day
        mes = dias.month
        ano = dias.year
        pgto = {'Cliente' : cliente,
                'Documento' : num,
                'Dia' : dia,
                'Mês' : mes,
                'Ano' : ano,
                'Veículo' : veiculo,
                'Placas' : placas, 
               'Forma Pagamento': pagou,
               'Valor' : valor,
               'Status' : 'Confirmado'}
        entry = [pgto]
        result = coll2.insert_many(entry)

def visualizar_pagamentos():
    pagamentos = db.pagamentos.find({})
    pagamentosdf = []
    for item in pagamentos:
        pagamentosdf.append(item)

    dfpgto = pd.DataFrame(pagamentosdf, columns= ['_id', 'Cliente','Documento', 'Veículo', 'Placas', 'Forma Pagamento', 'Valor', 'Status', 'Dia', 'Mês', 'Ano'])
    dfpgto.drop(columns='_id', inplace=True)
    st.session_state['pagamentos'] = dfpgto
    dfpgto = st.session_state['pagamentos']
    dfveic = st.session_state['veiculos']
    df_pagamento = pd.merge(dfveic, dfpgto, on="Placas", how='outer')
    padronizar_df(df_pagamento)
    st.session_state['df_pagamento'] = df_pagamento
    df = st.session_state['df_pagamento']
    #st.dataframe(df)

def padronizar_df(df):
    df.drop(columns= ['Documento_y','Cliente_y','Veículo_y'], inplace=True)
    df.rename(columns={'Documento_x' : 'Documento','Cliente_x' : 'Cliente', 'Veículo_x' : 'Veículo','Ano_x' : 'Ano Veic.', 'Ano_y':'Ano'}, inplace= True)
    df['Status'] = df['Status'].fillna('Pendente')
    #df['Status'].fillna('Pendente', inplace= True)
    #df['Data'] = df['Data'].fillna('0000-00-00')
    #df['Data'].fillna('0000-00-00', inplace= True)
    df['Forma Pagamento'] = df['Forma Pagamento'].fillna('Nenhum')
    #df['Forma Pagamento'].fillna('Nenhum', inplace= True)
    df['Valor'] = df['Valor'].fillna(0)
    #df['Valor'].fillna(0, inplace= True)
    return df

def supervisionar_pagamentos():
    df = st.session_state['df_pagamento']
    mes = {1: 'Janeiro', 2 :'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6 : 'Junho', 7 : 'Julho', 8 : 'Agosto', 9 : 'Setembro', 10 : 'Outubro', 11 : 'Novembro', 12 : 'Dezembro'}
    df['Mês'] = df['Mês'].map(mes)
    
    #col1,col2,col3,col4,col5 = st.columns(5)
    #ano = df['Ano'].value_counts().index
    #anos = col1.selectbox('Ano', ano)
    #df_ano = df[df['Ano'] == anos]
    #mes = df_ano['Mês'].value_counts().index
    #meses = col2.selectbox('Mês', mes)
    #df_mes = df_ano[df_ano['Mês'] == meses]
    #if meses not in mes:
    #    pass
    #else:
    #    df_mes_filtro = df_mes[['Cliente', 'Documento', 'N° Doc', 'Forma Pagamento', 'Valor', 'Dia', 'Veículo', 'Placas']]
    #    df_mes_filtro = df_mes_filtro[df_mes_filtro['Valor'] > 0] 
        #st.dataframe(df_mes_filtro)
    
def status_pagamento():
    df = st.session_state['df_pagamento']
    col1,col2 = st.columns(2)
    ano = df['Ano'].value_counts().index
    anos = col1.selectbox('A', ano, label_visibility='hidden')
    df_ano = df[df['Ano'] == anos]

    mes = df_ano['Mês'].value_counts().index
    meses = col2.selectbox('M', mes, label_visibility='hidden')
    df_mes = df_ano[df_ano['Mês'] == meses]
    df_status = df_mes[['Cliente', 'Veículo', 'Placas', 'Status']]

    col1, col2 = st.columns(2)
    df_status_ok = df_status[df_status['Status'] == 'Confirmado']
    df_status_ok = df_status_ok[['Cliente', 'Veículo', 'Placas']]
    st.session_state['df_status_ok'] = df_status_ok
    col1.header('**Pagamento Confirmado**')
    col1.dataframe(df_status_ok)

    df_status_nihil = df[~df['Placas'].isin(df_mes['Placas'])]
    df_status_nihil = df_status_nihil[['Cliente', 'Veículo', 'Placas', 'Status']]
    st.session_state['df_status_nihil'] = df_status_nihil
    col2.header('**Pagamento Pendente**')
    col2.dataframe(df_status_nihil[['Cliente', 'Veículo', 'Placas']])   

def analise_operacional():
    df = st.session_state['veiculos']
    veiculos_cadastrados = df['Placas'].value_counts().sum()
    
    clientes_cadastrados = df['Cliente'].nunique()

    df_pgto = st.session_state['df_pagamento']

    forma_pagamento = df_pgto['Forma Pagamento'].value_counts().index[0]
    tipo = df_pgto['Tipo'].value_counts().index[0]
    receita = df_pgto['Valor'].sum()

    col1,col2,col3,col4 = st.columns(4)
    col1.metric('Veículos Cadastrados:', veiculos_cadastrados)
    col2.metric('Clientes_cadastrados:', clientes_cadastrados)
    col3.metric('Tipo de veículo com mais rastreadores', tipo)
    col4.metric('Forma de pagamento mais utilizada', forma_pagamento)

    ano = df_pgto['Ano'].value_counts().index
    anos = col1.selectbox('Ano', ano)
    df_pgto_ano = df_pgto[df_pgto['Ano'] == anos]
    
    mes = df_pgto_ano['Mês'].value_counts().index
    meses = col2.selectbox('Mês', mes)

    df_pgto_mes = df_pgto_ano[df_pgto_ano['Mês'] == meses]
    df_status = df_pgto_mes[['Cliente', 'Veículo', 'Placas', 'Status']]
    df_status_ok = df_status[df_status['Status'] == 'Confirmado']
    df_status_ok = df_status_ok[['Cliente', 'Veículo', 'Placas']]
    df_status_nihil = df_pgto[~df_pgto['Placas'].isin(df_pgto_mes['Placas'])]
    df_status_nihil = df_status_nihil[['Cliente', 'Veículo', 'Placas']]

    soma_pagamento = df_pgto_mes['Valor'].sum()
    col1.metric('Receita mês:', f'R$ {soma_pagamento:,.2f}')
    veiculos_confirmados = df_status_ok['Placas'].value_counts().sum()
    col2.metric('Pagamentos confirmados:', veiculos_confirmados)
    col3.divider()
    veiculos_pendentes = df_status_nihil['Placas'].value_counts().sum()
    col3.metric('Pagamentos pendentes:', veiculos_pendentes)
    col4.divider()
    
def pagina_principal():
    visualizar_veiculos()
    visualizar_pagamentos()
    supervisionar_pagamentos()
    st.title('Sat 🌎')
    btn = authenticator.logout()
    if btn:
        st.session_state["authentication_status"] == None
    tab1,tab2,tab3 = st.tabs(['Análise', 'Clientes','Pagamentos'])
    with tab1:
        st.header('**Análise geral**')
        analise_operacional()
        
    with tab2:
        st.header('**Cadastro de Clientes**')
        cadastrar_veiculos()
        df = st.session_state['veiculos']
        st.dataframe(df)
    
    with tab3:
        st.header('**Pagamento**')
        pagamento_veiculos()
        st.divider()
        status_pagamento()
        

    #st.divider()
    #st.header('**Visulizando pagamentos**')
    #visualizar_pagamentos()

    #st.divider()
    #st.header('**Pagamentos**')
    #supervisionar_pagamentos()
    #st.divider()
    #status_pagamento()

    #st.divider()
    #st.header('**Análise geral**')
    #analise_operacional()    

def main():
    if st.session_state["authentication_status"]:
        pagina_principal()
    elif st.session_state["authentication_status"] == False:
        st.error("Username/password is incorrect.")

    elif st.session_state["authentication_status"] == None:
        st.warning("Please insert username and password")

if __name__ == '__main__':
    main()
