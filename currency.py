import streamlit as st
import pandas as pd
import numpy as np
from evds import evdsAPI
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from scipy.stats import zscore
import os

# API anahtarını çevre değişkenlerinden alma
os.environ["API_KEY"] = st.secrets["API_KEY"]
API_KEY = st.secrets["API_KEY"]
evds = evdsAPI(API_KEY)

# Başlık
st.title("Döviz Analizi ve Grafikler (TCMB)")

# Tarih aralığı seçimi
st.sidebar.header("Tarih Aralığı Seçimi")
today = datetime.now()

# Tarih aralığı seçenekleri
time_ranges = {
    "Son 1 Ay": today - timedelta(days=30),
    "Son 3 Ay": today - timedelta(days=90),
    "Son 6 Ay": today - timedelta(days=180),
    "Son 1 Yıl": today - timedelta(days=365),
    "Son 5 Yıl": today - timedelta(days=5 * 365),
    "Son 10 Yıl": today - timedelta(days=10 * 365),
}
selected_range = st.sidebar.selectbox("Zaman Aralığını Seçin", list(time_ranges.keys()))
start_date = time_ranges[selected_range]
end_date = today

# Buton aracılığıyla verilerin yüklenmesi
if st.sidebar.button("Verileri Getir"):
    # Tarihleri uygun formata dönüştürme
    start_date_str = start_date.strftime("%d-%m-%Y")
    end_date_str = end_date.strftime("%d-%m-%Y")

    try:
        # Veri çekme ve hata kontrolü
        with st.spinner("Veriler çekiliyor..."):
            data = evds.get_data(
                ['TP.DK.USD.A.YTL', 'TP.DK.USD.S.YTL', 'TP.DK.CNY.A.YTL', 'TP.DK.CNY.S.YTL'],
                startdate=start_date_str,
                enddate=end_date_str,
            )

            # DataFrame'e dönüştürme
            df = pd.DataFrame(data)

            # Tarih sütununu datetime formatına dönüştürme
            df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y')

            # NaN değerlerini lineer interpolasyon ile doldurma
            for col in ['TP_DK_USD_A_YTL', 'TP_DK_USD_S_YTL', 'TP_DK_CNY_A_YTL', 'TP_DK_CNY_S_YTL']:
                df[col] = df[col].interpolate()

            # Günlük Getiriler
            df['USD_Getiri'] = df['TP_DK_USD_S_YTL'].pct_change()
            df['CNY_Getiri'] = df['TP_DK_CNY_S_YTL'].pct_change()

            # Volatilite Hesaplama (Yıllık Volatilite için her yıl hesaplanacak)
            df['Year'] = df['Tarih'].dt.year
            usd_volatility = df.groupby('Year')['USD_Getiri'].std() * np.sqrt(252)  # Yıllık volatilite
            cny_volatility = df.groupby('Year')['CNY_Getiri'].std() * np.sqrt(252)

            # Mevsimsellik Analizi
            df['Ay'] = df['Tarih'].dt.month
            monthly_avg_usd = df.groupby('Ay')['TP_DK_USD_S_YTL'].mean()
            monthly_avg_cny = df.groupby('Ay')['TP_DK_CNY_S_YTL'].mean()

            # Şok Analizi
            df['USD_Getiri_ZScore'] = zscore(df['USD_Getiri'].dropna())
            df['CNY_Getiri_ZScore'] = zscore(df['CNY_Getiri'].dropna())
            shock_threshold = 2  # Eşik değer
            usd_shocks = df[df['USD_Getiri_ZScore'].abs() > shock_threshold]
            cny_shocks = df[df['CNY_Getiri_ZScore'].abs() > shock_threshold]

            # Column düzeni: 2 sütun
            col1, col2 = st.columns(2)

            # Dolar Analiz (Col1)
            with col1:
                # En güncel dolar değeri
                last_usd_value = df['TP_DK_USD_S_YTL'].iloc[-1]
                last_usd_previous = df['TP_DK_USD_S_YTL'].iloc[-2]
                usd_change = ((last_usd_value - last_usd_previous) / last_usd_previous) * 100  # Yüzde değişim

                st.metric("Güncel Dolar Kuru (TL)", f"{last_usd_value:.2f} TL", f"{usd_change:.2f}% değişim")

                # Dolar ve Çin Yuanı Satış Kuru Grafiği
                fig1 = go.Figure()
                fig1.add_trace(go.Scatter(x=df['Tarih'], y=df['TP_DK_USD_S_YTL'], mode='lines', name='Dolar Satış Kuru', line=dict(color='blue')))
                fig1.update_layout(title="Dolar Satış Kuru", xaxis_title="Tarih", yaxis_title="Türk Lirası (TL)", template="plotly_dark")
                st.plotly_chart(fig1, use_container_width=True)

                # Dolar Mevsimsellik Grafiği
                fig2 = px.bar(
                    x=monthly_avg_usd.index,
                    y=monthly_avg_usd.values,
                    labels={'x': 'Ay', 'y': 'Ortalama Kurlar'},
                    title="Dolar Mevsimsellik Analizi"
                )
                st.plotly_chart(fig2, use_container_width=True)

                # Dolar Şok Analizi
                fig4 = go.Figure()
                fig4.add_trace(go.Scatter(x=df['Tarih'], y=df['USD_Getiri_ZScore'], mode='lines', name='Dolar Z-Skor'))
                fig4.add_trace(go.Scatter(x=usd_shocks['Tarih'], y=usd_shocks['USD_Getiri_ZScore'], mode='markers', name='Şoklar', marker=dict(color='red', size=8)))
                fig4.update_layout(title="Dolar Şok Analizi (Z-Skor)", xaxis_title="Tarih", yaxis_title="Z-Skor", template="plotly_dark")
                st.plotly_chart(fig4, use_container_width=True)

                # Dolar Volatilite
                st.subheader("Dolar Volatilite (Yıllık)")
                st.write(f"Yıllık Volatilite Değeri:")
                st.dataframe(usd_volatility)

                # Dolar Volatilite Tablosu
                volatility_usd_table = pd.DataFrame({
                    'Yıl': usd_volatility.index,
                    'Volatilite': usd_volatility.values
                })
                st.write("Dolar Volatilite Tablosu:")
                st.dataframe(volatility_usd_table)

                # Dolar Şok Etkileri Tablosu
                st.subheader("Dolar Şok Etkileri Tablosu")
                shock_usd_table = usd_shocks[['Tarih', 'USD_Getiri_ZScore']]
                st.write("Dolar Şok Etkileri:")
                st.dataframe(shock_usd_table)

            # Çin Yuanı Analiz (Col2)
            with col2:
                # En güncel Çin Yuanı değeri
                last_cny_value = df['TP_DK_CNY_S_YTL'].iloc[-1]
                last_cny_previous = df['TP_DK_CNY_S_YTL'].iloc[-2]
                cny_change = ((last_cny_value - last_cny_previous) / last_cny_previous) * 100  # Yüzde değişim

                st.metric("Güncel Çin Yuanı Kuru (TL)", f"{last_cny_value:.2f} TL", f"{cny_change:.2f}% değişim")

                # Çin Yuanı Satış Kuru Grafiği
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=df['Tarih'], y=df['TP_DK_CNY_S_YTL'], mode='lines', name='Çin Yuanı Satış Kuru', line=dict(color='green')))
                fig3.update_layout(title="Çin Yuanı Satış Kuru", xaxis_title="Tarih", yaxis_title="Türk Lirası (TL)", template="plotly_dark")
                st.plotly_chart(fig3, use_container_width=True)

                # Çin Yuanı Mevsimsellik Grafiği
                fig5 = px.bar(
                    x=monthly_avg_cny.index,
                    y=monthly_avg_cny.values,
                    labels={'x': 'Ay', 'y': 'Ortalama Kurlar'},
                    title="Çin Yuanı Mevsimsellik Analizi"
                )
                st.plotly_chart(fig5, use_container_width=True)

                # Çin Yuanı Şok Analizi
                fig6 = go.Figure()
                fig6.add_trace(go.Scatter(x=df['Tarih'], y=df['CNY_Getiri_ZScore'], mode='lines', name='Çin Yuanı Z-Skor'))
                fig6.add_trace(go.Scatter(x=cny_shocks['Tarih'], y=cny_shocks['CNY_Getiri_ZScore'], mode='markers', name='Şoklar', marker=dict(color='red', size=8)))
                fig6.update_layout(title="Çin Yuanı Şok Analizi (Z-Skor)", xaxis_title="Tarih", yaxis_title="Z-Skor", template="plotly_dark")
                st.plotly_chart(fig6, use_container_width=True)

                # Çin Yuanı Volatilite
                st.subheader("Çin Yuanı Volatilite (Yıllık)")
                st.write(f"Yıllık Volatilite Değeri:")
                st.dataframe(cny_volatility)

                # Çin Yuanı Volatilite Tablosu
                volatility_cny_table = pd.DataFrame({
                    'Yıl': cny_volatility.index,
                    'Volatilite': cny_volatility.values
                })
                st.write("Çin Yuanı Volatilite Tablosu:")
                st.dataframe(volatility_cny_table)

                # Çin Yuanı Şok Etkileri Tablosu
                st.subheader("Çin Yuanı Şok Etkileri Tablosu")
                shock_cny_table = cny_shocks[['Tarih', 'CNY_Getiri_ZScore']]
                st.write("Çin Yuanı Şok Etkileri:")
                st.dataframe(shock_cny_table)
    except Exception as e:
        st.error(f"Veri alınırken bir hata oluştu: {str(e)}")
else:
    st.sidebar.info("Verileri görmek için tarih aralığını seçin ve 'Verileri Getir' butonuna basın.")
