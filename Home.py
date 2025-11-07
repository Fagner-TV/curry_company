import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home', page_icon= '🐼')

image_path = 'Ciclo/alvo.png'
image = Image.open(image_path)
st.sidebar.image(image,width=120)

st.header('Cury Company')
st.sidebar.markdown('Fastesty Delivey in Town')
st.sidebar.markdown('''___''')

st.write('Curry Company Growth Dashboard')

st.markdown( 
            """
            Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
            ### Como utilizar esse Growth Dashboard?
            
            - Visão Empresa
             
             -Visão Gerencial: Métricas gerenciais de comportamento.
             
             -Visão Tática: Indicadores semanais de crescimento. 
             
             -Visão Geográfica: Insights de geolocalização.
            
            -Visão Entregado:
             - Acompanhamento de indicadores semanais de crescimento.
            - Visão Restaurante:
             - Indicadores semanais de crescimento dos restaurantes. 
            ### Ask For Help 
            - Time de Data Science no Discord
             - @fagner

""")

