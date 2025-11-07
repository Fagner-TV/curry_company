#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
#bliblioteca necessária
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np
st.set_page_config(page_title='Visão Empresa', page_icon= '📉', layout='wide')
#----------------------------
#Funções
#----------------------------
def country_maps(df1):
  data_plot = df1[['Delivery_location_latitude','Delivery_location_longitude','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).median().reset_index()
  mapa = folium.Map()
  for index, location_info in data_plot.iterrows():
    folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
                  popup = location_info[['City','Road_traffic_density']]).add_to(mapa)
  folium_static(mapa,width=1024,height=600)   

def order_share_by_week(df1):
  df1_aux = df1[['ID','week_of_year']].groupby('week_of_year').count().reset_index()
  df2_aux = df1[["Delivery_person_ID",'week_of_year']].groupby('week_of_year').nunique().reset_index()
  dfx_aux = pd.merge(df1_aux,df2_aux, how='inner')
  dfx_aux ['order_by_delivery'] = dfx_aux['ID']/dfx_aux['Delivery_person_ID']
  fig = px.line(dfx_aux, x='week_of_year', y = 'order_by_delivery')
  return fig

def order_by_week(df1):
  df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
  df1_aux = df1[['ID','week_of_year']].groupby(['week_of_year']).count().reset_index()
  fig = px.line(df1_aux, x = 'week_of_year',y ='ID')
  return fig 

def traffic_order_city(df1):
  df_aux = df1[['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
  df_aux ['perct_ID'] = 100 * (df_aux['ID']/ df_aux['ID'].sum())
  fig = px.bar(df_aux, x="City", y='ID',color = 'Road_traffic_density', barmode = 'group')
  return fig

def traficc_order_share(df1): 
  df_aux = df1[['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
  df_aux['df1_porct'] = 100 * (df_aux['ID']/ df_aux['ID'].sum())
  fig = px.pie(df_aux, values = 'df1_porct', names = 'Road_traffic_density')
  return fig

def order_metric(df1): 
  #Order Metric
  df1_aux = df1[['ID','Order_Date']].groupby(['Order_Date']).count().reset_index()
  fig = px.bar(df1_aux, x = 'Order_Date', y ='ID')
  return fig

def clean_code(df1):
    """
    Esta função tem a responsabilidade de limpar o DataFrame:
    1. Remover dados 'NaN'
    2. Remover espaços em strings
    3. Converter texto para números inteiros e decimais
    4. Converter texto para datas
    5. Extrair números de colunas textuais (ex: 'Time_taken(min)')
    Input: DataFrame bruto
    Output: DataFrame limpo
    """

    # ---------------------------
    # 1. Remover espaços nas strings
    # ---------------------------
    cols_strip = ['ID', 'Road_traffic_density', 'Type_of_order',
                  'Type_of_vehicle', 'Festival', 'City', 'Weatherconditions']
    for col in cols_strip:
        if col in df1.columns:
            df1[col] = df1[col].astype(str).str.strip()

    # ---------------------------
    # 2. Substituir 'NaN' e 'NaN ' por np.nan e remover linhas vazias
    # ---------------------------
    df1.replace(['NaN', 'NaN '], np.nan, inplace=True)
    df1.dropna(how='any', inplace=True)

    # ---------------------------
    # 3. Conversões de tipo seguras
    # ---------------------------
    # Idade do entregador
    df1['Delivery_person_Age'] = pd.to_numeric(df1['Delivery_person_Age'], errors='coerce')
    # Avaliação
    df1['Delivery_person_Ratings'] = pd.to_numeric(df1['Delivery_person_Ratings'], errors='coerce')
    # Múltiplas entregas
    df1['multiple_deliveries'] = pd.to_numeric(df1['multiple_deliveries'], errors='coerce')

    # Remover linhas com dados inválidos nessas colunas
    df1.dropna(subset=['Delivery_person_Age', 'Delivery_person_Ratings', 'multiple_deliveries'], inplace=True)

    # Agora converter as colunas para o tipo correto
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # ---------------------------
    # 4. Conversão de texto para data
    # ---------------------------
    # Tenta converter com formato dia-mês-ano, e caso falhe, tenta ano-mês-dia
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y', errors='coerce')
    if df1['Order_Date'].isna().sum() > 0:
        df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%Y-%m-%d', errors='coerce')

    df1.dropna(subset=['Order_Date'], inplace=True)

    # ---------------------------
    # 5. Extrair apenas números de "Time_taken(min)"
    # ---------------------------
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).str.extract(r'(\d+)')
    df1['Time_taken(min)'] = pd.to_numeric(df1['Time_taken(min)'], errors='coerce')

    # ---------------------------
    # 6. Resetar o índice
    # ---------------------------
    df1.reset_index(drop=True, inplace=True)

    return df1

#------------------------------Inicio da estruturação dos dados------------------------------------
#--------------------------------------------------------------------------------------------------

#Import dataset

df = pd.read_csv('Ciclo/train.csv')

#Limpando os dados

df1 = clean_code(df)

#1.Visão empresa


#=====================================
#Barra Lateral
#=====================================
st.header("Marketplace - Visão Cliente")
image_path = 'Ciclo/alvo.png'
image = Image.open(image_path)
st.sidebar.image(image,width=120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?',value= datetime(2022,4,13),min_value= datetime(2022,2,11), max_value=datetime(2022,4,6), format='DD-MM-YYYY')

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',['Low','Medium','High','Jam'], default=['Low','Medium','High','Jam'])

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS')
#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]
#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]
#=====================================
#Layout Streamlit
#=====================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

# ==============================
# ABA 1 - Visão Gerencial
# ==============================
with tab1:
    with st.container():
        # Order Metric
        st.header('Orders by Day')  
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
 
    with st.container():    
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            fig = traficc_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)   

        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)       

# ==============================
# ABA 2 - Visão Tática
# ==============================
with tab2:
    with st.container(): 
        st.header('Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
  
    with st.container():
        st.header('Order Share by Week') 
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
    
# ==============================
# ABA 3 - Visão Geográfica
# ==============================
with tab3:
    st.header('Country Maps')
    country_maps(df1)