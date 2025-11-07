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
st.set_page_config(page_title='Visão Entregadores', page_icon= '🚗', layout='wide')

#-------------------------------------------
#Funções 
#-------------------------------------------
def avg_por_transito(df1): 
            df_avg_rating_by_traffic = ((df1[['Delivery_person_Ratings','Road_traffic_density']]
                                         .groupby('Road_traffic_density')
                                         .agg({'Delivery_person_Ratings':['mean','std']})))
            df_avg_rating_by_traffic.columns = ['delivery_mean','delivery_std']
            df_avg_rating_by_traffic.reset_index()
            st.dataframe(df_avg_rating_by_traffic)
            st.markdown('Avaliação média por clima')
            avg_clima = ((df1[['Delivery_person_Ratings','Weatherconditions']])
                         .groupby('Weatherconditions')
                         .agg({'Delivery_person_Ratings':['mean','std']}))
            # mudança de nome das colunas
            avg_clima.columns = ['Delivery_mean','Delivert_std'] 
            #reset do index
            avg_clima.reset_index() 
            return avg_clima
        
def top_delivers(df1, top_asc):
            aux = (df1.loc[:,['Time_taken(min)',"Delivery_person_ID",'City']]
                  .groupby(['City',"Delivery_person_ID"])
                  .max().sort_values(['Time_taken(min)'], ascending = top_asc).reset_index())
            aux_1 = aux.loc[aux['City'] == 'Metropolitian',:].head(10)
            aux_2 = aux.loc[aux['City'] == 'Urban',:].head(10)
            aux_3 = aux.loc[aux['City'] == 'Semi-Urban',:].head(10)
            df3 = pd.concat([aux_1,aux_2,aux_3]).reset_index(drop =True)
            return df3
        
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

#=====================================
#Barra Lateral
#=====================================
st.header("Marketplace - Visão Entregadores")
#image_path = 'Ciclo/alvo.png'
image = Image.open('Ciclo/alvo.png')
st.sidebar.image(image,width=120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual data ?',value= datetime(2022,4,13),min_value= datetime(2022,2,11), max_value=datetime(2022,4,6), format='DD-MM-YYYY')

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',['Low','Medium','High','Jam'], default=['Low','Medium','High','Jam'])
st.sidebar.markdown('''---''') 

conditions_options = st.sidebar.multiselect('Quais as condições climaticas',['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms','conditions Cloudy', 'conditions Fog', 'conditions Windy'], default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms','conditions Cloudy', 'conditions Fog', 'conditions Windy'])
st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comuidade DS')
#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]
#Filtro de transito
linhas_seelcionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]
#=====================================
#Layout Streamlit
#=====================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial',"-","-"])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4,gap='large')
        with col1:
             # Entregador com maior idade
            maior_idade = df1[['Delivery_person_Age']].max()
            col1.metric('Maior idade', maior_idade)
        with col2:
            # Entregador com menor idade
            menor_idade = df1[['Delivery_person_Age']].min()
            col2.metric('Menor idade',menor_idade)   
        with col3:
            # Melhor concição veículo
            melhor_condicao = df1[['Vehicle_condition']].max()
            col3.metric('Melhor condição',melhor_condicao)
        with col4:
            # Pior concição veículo
            pior_condicao = df1[['Vehicle_condition']].min()
            col4.metric('Pior condição', pior_condicao)
    with st.container():
        st.markdown('''---''') 
        st.title('Avaliações')   
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('Avaliação média por entregadores')
            avg_entrega = (df1[['Delivery_person_Ratings','Delivery_person_ID']]
             .groupby('Delivery_person_ID')
             .mean().sort_values('Delivery_person_Ratings',ascending = False)
             .reset_index())  
            st.dataframe(avg_entrega,height=480) 
        with col2:
            st.markdown('Avaliação média por transito')
            avg_clima = avg_por_transito(df1)
            st.dataframe(avg_clima)    
            
    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('Top entregadores mais rapidos')
            df3 = top_delivers(df1, top_asc = True) 
            st.dataframe(df3) 
            
        with col2:
            st.markdown('Top entregadores mais lentos')
            df3 = top_delivers(df1, top_asc = False)
            st.dataframe(df3)  
           
                     