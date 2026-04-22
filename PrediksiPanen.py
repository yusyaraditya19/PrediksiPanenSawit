import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# =========================
# CONFIG UI
# =========================
st.set_page_config(
    page_title='Dashboard Sawit',
    layout='wide',
    initial_sidebar_state='expanded'
)

# =========================
# CSS SIMPLE
# =========================
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fb;
    }
    div.block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
data = pd.read_csv('dataset_kelapa_sawit_500.csv')

# =========================
# SIDEBAR - CONTROL DASHBOARD
# =========================
st.sidebar.header('Kontrol Dashboard')

mode = st.sidebar.selectbox('Mode Tampilan', ['Ringkas', 'Lengkap'])

st.sidebar.subheader('Filter Data')

ndvi_min, ndvi_max = st.sidebar.slider(
    'Rentang NDVI',
    float(data['NDVI'].min()),
    float(data['NDVI'].max()),
    (float(data['NDVI'].min()), float(data['NDVI'].max()))
)

panen_min, panen_max = st.sidebar.slider(
    'Rentang Hasil Panen',
    float(data['Hasil_Panen_ton_per_ha'].min()),
    float(data['Hasil_Panen_ton_per_ha'].max()),
    (float(data['Hasil_Panen_ton_per_ha'].min()), float(data['Hasil_Panen_ton_per_ha'].max()))
)

# =========================
# APPLY FILTER
# =========================
data = data[
    (data['NDVI'] >= ndvi_min) &
    (data['NDVI'] <= ndvi_max) &
    (data['Hasil_Panen_ton_per_ha'] >= panen_min) &
    (data['Hasil_Panen_ton_per_ha'] <= panen_max)
]

# =========================
# HEADER
# =========================
st.title('Dashboard Prediksi Hasil Panen Kelapa Sawit')
st.info(
    "Dashboard ini digunakan untuk melakukan analisis data kelapa sawit serta prediksi hasil panen "
    "berdasarkan variabel yang tersedia dalam dataset. "
    "Seluruh visualisasi pada bagian analitik bersifat dinamis dan interaktif, serta akan diperbarui "
    "secara otomatis sesuai filter yang dipilih melalui sidebar. "
    "Mode tampilan digunakan untuk mengatur jumlah data yang ditampilkan (ringkas atau lengkap)."
)

st.divider()

# =========================
# KPI CARDS
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric('Total Data', len(data))

with col2:
    st.metric('Rata-rata Panen', round(data['Hasil_Panen_ton_per_ha'].mean(), 2))

with col3:
    st.metric('NDVI Max', round(data['NDVI'].max(), 2))

st.divider()

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs([
    'Data Overview',
    'Prediksi Data',
    'Dashboard Analitik'
])

# =========================
# TAB 1
# =========================
with tab1:
    st.subheader('Dataset Kelapa Sawit')

    if mode == 'Ringkas':
        st.dataframe(data.head(10), use_container_width=True)
    else:
        st.dataframe(data, use_container_width=True)

    st.dataframe(data.describe(), use_container_width=True)

# =========================
# TAB 2
# =========================
with tab2:
    st.subheader('Input Prediksi')

    c1, c2, c3 = st.columns(3)

    with c1:
        curah = st.number_input('Curah Hujan', 0)
        suhu = st.number_input('Suhu', 0)

    with c2:
        kelembaban = st.number_input('Kelembaban', 0)
        ndvi = st.number_input('NDVI', 0.0)

    with c3:
        lahan = st.number_input('Luas Lahan', 0.0)
        pupuk = st.number_input('Pupuk', 0)

    rata = data['Hasil_Panen_ton_per_ha'].mean()

    if st.button('Jalankan Prediksi'):

        skor = (curah + pupuk + lahan * 100) / 3

        st.subheader('Hasil Prediksi')

        c1, c2 = st.columns(2)

        with c1:
            if skor >= rata:
                st.success('Hasil Panen TINGGI')
            else:
                st.error('Hasil Panen RENDAH')

        with c2:
            st.metric('Skor', round(skor, 2))
            st.metric('Rata-rata', round(rata, 2))

        st.subheader('Perbandingan (Bar + Line)')

        fig, ax = plt.subplots()
        x = ['Rata-rata', 'Prediksi']
        y = [rata, skor]

        ax.bar(x, y)
        ax.plot(x, y, marker='o', color='red')
        st.pyplot(fig)

# =========================
# TAB 3 - ANALITIK
# =========================
with tab3:
    st.subheader('Analisis Data Keseluruhan')

    c1, c2 = st.columns(2)

    # HEATMAP + NILAI
    with c1:
        st.write('Heatmap Korelasi')

        corr = data.corr(numeric_only=True)

        fig, ax = plt.subplots()
        im = ax.imshow(corr)

        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha='right')
        ax.set_yticklabels(corr.columns)

        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                        ha='center', va='center', fontsize=7)

        fig.colorbar(im)
        st.pyplot(fig)

    # SCATTER + TREND LINE
    with c2:
        st.write('NDVI vs Hasil Panen (Trend Line)')

        x = data['NDVI']
        y = data['Hasil_Panen_ton_per_ha']

        fig2, ax2 = plt.subplots()
        ax2.scatter(x, y, alpha=0.5)

        if len(x) > 1:
            m, b = np.polyfit(x, y, 1)
            ax2.plot(x, m*x + b, color='red')

        st.pyplot(fig2)

    # HISTOGRAM + LINE
    st.write('Distribusi Hasil Panen')

    fig3, ax3 = plt.subplots()
    n, bins, patches = ax3.hist(data['Hasil_Panen_ton_per_ha'], bins=20)
    ax3.plot(bins[:-1], n, color='red')

    st.pyplot(fig3)