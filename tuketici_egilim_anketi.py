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
st.title("Tüketici Güven Endeksi (TCMB, TÜİK)")

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
    'TP.TG2.Y01': 'Tüketici Güven Endeksi (*)',
    'TP.TG2.Y02': 'Hanenin maddi durumu (12 ay öncesine göre mevcut dönemde)',
    'TP.TG2.Y03': 'Hanenin maddi durum beklentisi (gelecek 12 aylık dönemde)',
    'TP.TG2.Y04': 'Genel ekonomik durum (12 ay öncesine göre mevcut dönemde)',
    'TP.TG2.Y05': 'Genel ekonomik durum beklentisi (gelecek 12 aylık dönemde)',
    'TP.TG2.Y06': 'İşsizlerin sayısı beklentisi (gelecek 12 aylık dönemde)',
    'TP.TG2.Y07': 'Yarı-dayanıklı tüketim mallarına yönelik harcama yapma düşüncesi (geçen 3 aylık döneme göre gelecek 3 aylık dönemde)',
    'TP.TG2.Y08': 'Mevcut dönemin dayanıklı tüketim malı satın almak için uygunluğu',
    'TP.TG2.Y09': 'Dayanıklı tüketim mallarına yönelik harcama yapma düşüncesi (geçen 12 aylık döneme göre gelecek 12 aylık dönemde)',
    'TP.TG2.Y10': 'Mevcut dönemin tasarruf etmek için uygunluğu',
    'TP.TG2.Y11': 'Hanenin içinde bulunduğu mali durumu',
    'TP.TG2.Y12': 'Tasarruf etme ihtimali (gelecek 12 aylık dönemde)',
    'TP.TG2.Y13': 'Tüketimin finansmanı amacıyla borç kullanma ihtimali (gelecek 3 aylık dönemde)',
    'TP.TG2.Y14': 'Tüketici fiyatlarının değişimine ilişkin düşünce (geçen 12 aylık dönemde)',
    'TP.TG2.Y15': 'Tüketici fiyatlarının değişimine ilişkin beklenti (geçen 12 aylık döneme göre gelecek 12 aylık dönemde)',
    'TP.TG2.Y16': 'Ücretlerin değişimine ilişkin beklenti (geçen 12 aylık döneme göre gelecek 12 aylık dönemde)',
    'TP.TG2.Y17': 'Otomobil satın alma ihtimali (gelecek 12 aylık dönemde)',
    'TP.TG2.Y18': 'Konut tamiratına para harcama ihtimali (gelecek 12 aylık dönemde)',
    'TP.TG2.Y19': 'Konut satın alma veya inşa ettirme ihtimali (gelecek 12 aylık dönemde)',
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
                list(titles.keys()),  # Serilerin kodlarını listeliyoruz
                startdate=start_date_str,
                enddate=end_date_str,
            )

            # DataFrame'e dönüştürme
            df = pd.DataFrame(data)

            # DataFrame'in tarih sütununu dönüştürme
            df['Tarih'] = pd.to_datetime(df['Tarih'], format="%Y-%m")

            # Grafikleri oluştur
            for column in df.columns[1:]:
                # Seri adına göre başlık al
                title_key = column.replace("_", ".")  # 'TP_TG2_Y01' -> 'TP.TG2.Y01'
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
                
                # Grafik için bir expander oluşturma
                with st.expander(title):
                    st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Veri alınırken bir hata oluştu: {str(e)}")
else:
    st.sidebar.info("Verileri görmek için tarih aralığını seçin ve 'Verileri Getir' butonuna basın.")
