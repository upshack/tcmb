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
st.title("TÜİK ve İTO Fiyat Endeksleri Analizi")

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
    'bie_tukfiy4': 'TÜİK - Fiyat Endeksi (Tüketici) (2003=100)',
    'bie_feoktg': 'TÜİK - Fiyat Endeksi-Özel Kapsamlı TÜFE Göstergeleri (2003=100) (Yeni Seri)',
    'bie_tufe1yi': 'TÜİK - Fiyat Endeksi (Yurt İçi Üretici Fiyatları) (2003=100) (NACE REV.2)',
    'bie_ufeyd': 'TÜİK - Fiyat Endeksi (Yurt Dışı Üretici Fiyatları) (2010=100) (NACE REV.2)',
    'bie_ito68': 'İTO - Geçinme Endeksi (Ücretliler) (1968=100)',
    'bie_ito95': 'İTO - Geçinme Endeksi (Ücretliler) (1995=100)',
    'bie_itouge85': 'İTO - Geçinme Endeksi (Ücretliler)-İstanbul (1985=100)',
    'bie_itotefe': 'İTO - Fiyat Endeksi (Toptan Eşya) (1968=100)',
    'bie_itoteuc': 'İTO - Fiyat (Toptan Eşya) ve Geçinme (Ücretliler) Endeksleri-İstanbul',
    'bie_brentpetrol': 'Avrupa Brent Petrol Spot FOB Fiyatı (Varil Başına Dolar)',
    'bie_tarimufe': 'TÜİK - Tarım Ürünleri Üretici Fiyat Endeksi (2020=100)',
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
                title = titles.get(column, column)  # Başlık sözlüğünden başlık al
                
                # Grafik oluşturma
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['Tarih'], y=df[column], mode='lines+markers', name=title))
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
