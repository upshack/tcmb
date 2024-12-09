import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from evds import evdsAPI
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os 

st.set_page_config(layout="wide")
pages = {
    "Kur": [
        st.Page("currency.py", title="Kur Analizi"),
    ],
    "Enflasyon ve İlişkisel Veriler": [
        st.Page("sektorel_enflasyon_verileri.py", title="Sektörel Enflasyon Beklentileri"),
        st.Page("tuketici_egilim_anketi.py", title="Tüketici Eğilim Anketi"),
        st.Page("fiyat_endeksleri.py", title="Fiyat Endeksleri"),
    ],
}

pg = st.navigation(pages)
pg.run()