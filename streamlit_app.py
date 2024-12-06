import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from evds import evdsAPI
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os 

os.environ["API_KEY"] == st.secrets['API_KEY']
API_KEY = st.secrets['API_KEY']
evds = evdsAPI(API_KEY)
print(st.secrets)
# Veri çekme
data = evds.get_data(['TP.DK.USD.A.YTL', 'TP.DK.USD.S.YTL'], 
                     startdate="01-05-2024", enddate="30-11-2024")

# DataFrame'e dönüştürme
df = pd.DataFrame(data)

# Tarih sütununu datetime formatına dönüştürme
df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y')

# NaN değerlerini lineer interpolasyon ile doldurma
df['TP_DK_USD_A_YTL'] = df['TP_DK_USD_A_YTL'].interpolate()
df['TP_DK_USD_S_YTL'] = df['TP_DK_USD_S_YTL'].interpolate()

# Plotly grafik oluşturma
fig = go.Figure()

# Dolar alış kuru grafiği
fig.add_trace(go.Scatter(
    x=df['Tarih'],
    y=df['TP_DK_USD_A_YTL'],
    mode='lines',  # Sadece çizgiler
    name='Dolar Alış Kuru (YTL)',
    line=dict(color='blue')
))

# Dolar satış kuru grafiği
fig.add_trace(go.Scatter(
    x=df['Tarih'],
    y=df['TP_DK_USD_S_YTL'],
    mode='lines',  # Sadece çizgiler
    name='Dolar Satış Kuru (YTL)',
    line=dict(color='red')
))

# Grafik başlık ve düzenleme
fig.update_layout(
    title='Dolar Alış ve Satış Kuru Zaman Serisi (Mayıs-Kasım 2024)',
    xaxis_title='Tarih',
    yaxis_title='Kuruş (YTL)',
    legend_title="Kurlar",
    template='plotly_dark',
    xaxis=dict(
        tickformat='%d-%m-%Y',
        tickangle=45
    ),
    margin=dict(l=40, r=40, t=40, b=40)
)

# Streamlit başlık ve açıklama
st.title("Dolar Kuru Zaman Serisi Grafiği")
st.write("Aşağıdaki grafik Mayıs-Kasım 2024 tarihleri arasındaki dolar alış ve satış kurlarını göstermektedir.")

# Streamlit'te Plotly grafiği gösterme
st.plotly_chart(fig, use_container_width=True)