from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import numpy as np
#bliblioteca necessária
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
st.set_page_config(page_title='Visão Restaurante', page_icon= '☕', layout='wide')
#-------------------------------------------
#Funções 
#-------------------------------------------
def avg_std_city(df1):  
          avg_desvp = df1[['Time_taken(min)','City']].groupby('City').agg({'Time_taken(min)':['mean','std']})
          avg_desvp.columns = ['Time_mean','Time_desvp']
          avg_desvp = avg_desvp.reset_index()
          fig = go.Figure()
          fig.add_trace(go.Bar(name='Control', x=avg_desvp ['City'], y=avg_desvp['Time_mean'],error_y=dict(type = 'data',array=avg_desvp['Time_desvp'])))
          fig.update_layout(barmode='group')
          return fig

def time_avg_std_city_delivery(df1):    
          avg_desvp = df1[['Time_taken(min)','City','Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})
          avg_desvp.columns = ['Time_mean','Time_desvp']
          avg_desvp = avg_desvp.reset_index()
          return avg_desvp

def std_avg_delivery_city(df1):
             avg_desvp = df1[['Time_taken(min)','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
             avg_desvp.columns = ['Time_mean','Time_desvp']
             avg_desvp = avg_desvp.reset_index()
             fig = px.sunburst(avg_desvp,path=['City','Road_traffic_density'], values= 'Time_mean',color='Time_desvp',color_continuous_scale='RdBu_r', color_continuous_midpoint=np.average(avg_desvp['Time_desvp']))
             return fig

def avg_time_delivery(df1): 
         df1['Distancia'] = df1[['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )), axis = 1)
         avg_distancia = df1[['City','Distancia']].groupby('City').mean().reset_index()
         fig = go.Figure(data=[go.Pie(labels= avg_distancia['City'],values = avg_distancia['Distancia'], pull = [0,0.1,0])])
         return fig


def avg_std_time_delivery(df1,festival,op):
            #'''
            #Esta função calcula o tempo e o desvio padrão do tempo de entrega.
            #Parâmetros:
            # - Input:
            # - df: Dataframe, dados necessários para o cálculo
            # - op: Tipo de operação que deve ser realizada
            # - 'avg_Time': Calcula  a média do tempo
            # - 'Std_Time': Calcula o desvio padrão do tempo   
            # - Output:
            # df: Dataframe com duas coluna e uma linha
            #'''   
            entrega_mean = df1[['Time_taken(min)','Festival']].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
            entrega_mean.columns = ['avg_Time', 'Std_Time']
            entrega_mean = entrega_mean.reset_index()
            entrega_mean = np.round(entrega_mean.loc[entrega_mean['Festival'] == festival, op],2)
            return entrega_mean

def distancia(df1): 
            df1['Distancia'] = df1[['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )), axis = 1)
            avg_distancia = np.round(df1['Distancia'].mean(),2)
            return avg_distancia
        
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
image_path = 'Ciclo/alvo.png'
image = Image.open(image_path)
st.sidebar.image(image,width=120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual data ?',value= datetime(2022,4,13),min_value= datetime(2022,2,11), max_value=datetime(2022,4,6), format='DD-MM-YYYY')

st.sidebar.markdown('''---''')
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',['Low','Medium','High','Jam'], default=['Low','Medium','High','Jam'])
st.sidebar.markdown('''---''') 
traffic_options = st.sidebar.multiselect('Qual a Cidade ?',['Metropolitian','Semi-Urban','Urban'], default=['Metropolitian','Semi-Urban','Urban'])
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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
    
    with st.container():
        st.title('Overal Metrics')
        col1,col2,col3 =st.columns(3)
        with col1:
            entregadores_unicos = len(df1['Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos',entregadores_unicos)
        with col2:
            avg_distancia = distancia(df1)
            col2.metric('A distância média das entregas', avg_distancia)
            
        with col3:
            entrega_mean = avg_std_time_delivery(df1, 'Yes', 'avg_Time')
            col3.metric('Tempo médio c/Festival',entrega_mean)  
            
    with st.container():
        st.markdown('''___''')
        col1,col2,col3 = st.columns (3) 
        with col1:
            entrega_mean = avg_std_time_delivery(df1,'Yes','Std_Time' )
            col1.metric('Tempo Dv.Padrão c/Festival',entrega_mean) 
           
        with col2:
            entrega_mean = avg_std_time_delivery(df1,'No','avg_Time')
            col2.metric('Tempo médio S/Festival',entrega_mean)
        with col3:
            entrega_mean = avg_std_time_delivery(df1,'No','Std_Time')
            col3.metric('Tempo Dv.Padrão s/Festival',entrega_mean)        
    
    with st.container():
        st.markdown('''___''')
        col1,col2 = st.columns(2)
        with col1:
         fig = avg_time_delivery(df1)
         st.header('Tempo médio de entrega por cidade')
         st.plotly_chart(fig)
        with col2:
         st.header('Tempo médio e Dv.Padrão de entrega por cidade e tipo de tráfego')
         fig = std_avg_delivery_city(df1)
         st.plotly_chart(fig)
             
    with st.container():
        st.markdown('''___''')
        col1,col2 = st.columns(2)
        with col1:
         st.header("Tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.")
         avg_desvp = time_avg_std_city_delivery(df1)
         st.dataframe(avg_desvp)       
         
        with col2:
         st.header('O tempo médio e o desvio padrão de entrega por cidade')
         fig = avg_std_city(df1) 
         st.plotly_chart(fig) 

          
