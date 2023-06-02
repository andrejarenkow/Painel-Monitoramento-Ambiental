#Dashboard com dados da covid no esgoto ETE Serraria

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# Configurações da página
st.set_page_config(
    page_title="Painel Monitoramnto Ambiental",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Título principal do painel
st.columns([1.5,7,1])[1].subheader("Painel de Monitoramento Ambiental do SARS-CoV-2 no Rio Grande do Sul, Brasil")

# Barra lateral para seleção de filtros
with st.sidebar:
    st.write('Selecione os filtros!')
    data_inicial = st.date_input(
        "Data inicial",
        datetime.date(2020, 5, 1))

    data_final = st.date_input(
        "Data inicial",
        datetime.date.today())

# Texto de introdução
texto = """ 
O monitoramento ambiental do novo coronavírus (SARS-COV2) em águas residuárias
e de superficie do Rio Grande do Sul é uma pesquisa de vigilância ambiental,
coordenado pelo Centro Estadual de Vigilância em Saúde (Cevs),
em parceria com diversas instituições.

Tem como objetivo disponibilizar informações sobre a circulação do vírus nas diferentes áreas do território avaliado.
Abaixo você pode verificar os dados disponíveis sobre o projeto.
\n
\n
"""
with st.container():
    st.markdown('**O que é o monitoramento ambiental?**')
    st.markdown(texto)

# Divisão de colunas
col2, col3 = st.columns([2,3])

# Carregando os dados de carga viral
carga_viral = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vTZfjxdY8_x5WNd9_NE3QQPeche-dMdY5KdvNpq8H4W-lmUTidwrKpV0uLzLtihV7UAPIl68WvugMsN/pub?gid=0&single=true&output=csv')
carga_viral['Data de coleta'] = pd.to_datetime(carga_viral['Data de coleta'], dayfirst=True).dt.date
carga_viral = carga_viral.dropna(subset=['Data de coleta'])
carga_viral = carga_viral[carga_viral['Local de coleta']=='ETE Serraria']
carga_viral['carga_viral_n1'] = pd.to_numeric(carga_viral['carga_viral_n1'] , errors='coerce')

# Carregando os dados de casos diários
casos = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vTZfjxdY8_x5WNd9_NE3QQPeche-dMdY5KdvNpq8H4W-lmUTidwrKpV0uLzLtihV7UAPIl68WvugMsN/pub?gid=1012737506&single=true&output=csv')
casos['Data sintomas'] = pd.to_datetime(casos['Data sintomas'], dayfirst=True).dt.date
casos = casos[casos['Município'] == 'PORTO ALEGRE']

# Aplicando os filtros ao período escolhido
casos_grafico = casos[(casos['Data sintomas']>data_inicial)&(casos['Data sintomas']<data_final)]
carga_viral_grafico = carga_viral[(carga_viral['Data de coleta']>data_inicial)&(carga_viral['Data de coleta']<data_final)]

# Criando os gráficos
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(x=casos_grafico['Data sintomas'], y=casos_grafico['Casos'], name="Casos diários", mode="lines"),
    secondary_y=True
)

fig.add_trace(
    go.Bar(x=carga_viral_grafico['Data de coleta'], y=carga_viral_grafico['carga_viral_n1'], name="Carga Viral no esgoto"),
    secondary_y=False
)

fig.update_xaxes(title_text="Data")

# Definindo os títulos dos eixos y
fig.update_yaxes(title_text="Carga viral", secondary_y=False, range=[0,carga_viral_grafico['carga_viral_n1'].max()+100])
fig.update_yaxes(title_text="Casos diários", secondary_y=True, range=[0,casos_grafico['Casos'].max()+100])

# Adicionando o título do gráfico
fig.update_layout(
    title_text="Casos diários de COVID e Carga Viral de SARS-CoV-2 no Esgoto na ETE Serraria, Porto Alegre, 2023", 
)

# Conversão do DataFrame para CSV
@st.cache_data
def convert_df(df):
    # IMPORTANTE: Cacheie a conversão para evitar o cálculo a cada execução
    return df.to_csv().encode('utf-8')

csv = convert_df(carga_viral_grafico)

# Coluna da direita - Métricas
with col2:
    media_ultimo_resultado = int((carga_viral['carga_viral_n1'].iloc[-1] + carga_viral['carga_viral_n1'].iloc[-2])/2)
    media_penultimo_resultado = int((carga_viral['carga_viral_n1'].iloc[-3] + carga_viral['carga_viral_n1'].iloc[-4])/2)
    metrica1, metrica2, metrica3 = st.columns(3)
    with metrica1:
        st.metric('Média da Carga Viral', "{:,}".format(media_ultimo_resultado), "{:,}".format(media_ultimo_resultado - media_penultimo_resultado), delta_color='inverse')
    with metrica2:
        st.metric('Máximo carga viral', "{:,}".format(int(carga_viral_grafico['carga_viral_n1'].max())))
    with metrica3:
        st.metric('Maior número de casos', "{:,}".format(int(casos_grafico['Casos'].max())))

    st.download_button(
        label="Baixar dados da carga viral em CSV",
        data=csv,
        file_name='dados_carga_viral.csv',
        mime='text/csv',
    )
