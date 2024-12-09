import streamlit as st
from evds import evdsAPI
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os

# API anahtarını çevre değişkenlerinden alma
os.environ["API_KEY"] = st.secrets["API_KEY"]
API_KEY = st.secrets["API_KEY"]
evds = evdsAPI(API_KEY)

# Başlık
st.title("Sektörel Enflasyon Beklentileri (TCMB, TÜİK)")

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

# Başlıklar ile seri isimlerini eşleştir
titles = {
    'TP.ENFBEK.PKA12ENF': 'Piyasa katılımcılarının 12 ay sonrası yıllık enflasyon beklentileri (%)',
    'TP.ENFBEK.IYA12ENF': 'Reel sektörün 12 ay sonrası yıllık enflasyon beklentileri (%)',
    'TP.ENFBEK.TEA12ENF': 'Hanehalkının 12 ay sonrası yıllık enflasyon beklentileri (%)',
    'TP.ENFBEK.TEA12': 'Tüketici fiyatlarının daha hızlı veya aynı oranda artacağını bekleyen hanehalkı oranı (%)',
    'TP.ENFBEK.TEA345': 'Tüketici fiyatlarının aynı kalacağını, düşeceğini veya daha düşük bir oranla artacağını bekleyen hanehalkı oranı (%)'
}

# Veri çekme ve grafik oluşturma işlemi
if st.sidebar.button("Verileri Getir"):
    # Tarihleri uygun formata dönüştürme
    start_date_str = start_date.strftime("%d-%m-%Y")
    end_date_str = end_date.strftime("%d-%m-%Y")

    try:
        with st.spinner("Veriler çekiliyor..."):
            # Verileri çek
            data = evds.get_data(
                list(titles.keys()),
                startdate=start_date_str,
                enddate=end_date_str,
            )

            # DataFrame'e dönüştürme
            df = pd.DataFrame(data)

            # DataFrame'in tarih sütununu dönüştürme
            df['Tarih'] = pd.to_datetime(df['Tarih'], format="%Y-%m")

            # Grafikleri oluştur ve expander içinde göster
            for column in df.columns[1:]:
                # Seri adına göre başlık al
                title_key = column.replace("_", ".")  # 'TP_ENFBEK_PKA12ENF' -> 'TP.ENFBEK.PKA12ENF'
                title = titles.get(title_key, column)  # Başlık sözlüğünden başlık al
                
                # Grafik oluşturma
                fig = go.Figure()
                fig.add_trace(go.Bar(x=df['Tarih'], y=df[column], name=title))
                fig.update_layout(
                    title=f"{title}",
                    xaxis_title="Tarih",
                    yaxis_title="Değer",
                    template="plotly_dark"
                )

                # Grafik için expander oluşturma
                with st.expander(title):
                    st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Veri alınırken bir hata oluştu: {str(e)}")
else:
    st.sidebar.info("Verileri görmek için tarih aralığını seçin ve 'Verileri Getir' butonuna basın.")
