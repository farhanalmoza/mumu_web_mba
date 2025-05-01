import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Unduh file CSV dari Google Drive
output = 'data.csv'  # nama file setelah diunduh
df = pd.read_csv(output)

# Memilih hanya kolom yang dibutuhkan
df_selected = df.iloc[:, [0, 1, 2, 3, 4, 5]]

# Mengubah tipe data kolom 'pcs' agar mendukung angka desimal (float)
df_selected['pcs'] = pd.to_numeric(df_selected['pcs'], errors='coerce')
cleaned = df_selected.dropna()

# Langkah 1: Ubah tipe data dari float ke int
cleaned['date'] = cleaned['date'].astype(int)

# Langkah 2: Ubah ke string
cleaned['date'] = cleaned['date'].astype(str)

# Langkah 3: Format ulang menjadi YYYYMMDD
def format_date(date_str):
    if len(date_str) == 6:
        year = '20' + date_str[:2]  # Tahun 2000-an
        month_day = date_str[2:]     # Bulan dan hari
        return year + month_day
    return date_str  # Kembalikan nilai asli jika tidak sesuai

cleaned['date'] = cleaned['date'].apply(format_date)

# Langkah 4: Konversi ke tipe data tanggal
cleaned['date'] = pd.to_datetime(cleaned['date'], format='%Y%m%d', errors='coerce')

cleaned['-'] = cleaned['-'].astype(int)
cleaned['kode_barang'] = cleaned['kode_barang'].astype(int)
cleaned['TRX_ID'] = cleaned['TRX_ID'].astype(int)
cleaned['nama_barang'] = cleaned['nama_barang'].astype(str)

df_sorted = cleaned.groupby('TRX_ID', group_keys=False).apply(lambda x: x.sort_values('nama_barang'))
trx_count = len(df_sorted)
item_count = len(pd.unique(df_sorted['nama_barang']))


# TOP 5 TRANSACTION
count = df_sorted['nama_barang'].value_counts().reset_index()
count.columns = ['nama_barang', 'jumlah_transaksi']

# Mengambil 5 produk dengan jumlah transaksi tertinggi
top_5 = count.nlargest(5, 'jumlah_transaksi')
# Agar cocok dengan st.bar_chart, set index ke nama barang
top_5_chart = top_5.set_index('nama_barang')


# STYLE
# CSS custom untuk styling kartu
st.markdown("""
    <style>
    .card {
        background-color: #f4efe3;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin: 10px;
    }
    .card-number {
        color: #f45b22;
        font-size: 30px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .card-label {
        color: #1e3a5f;
        font-size: 14px;
        font-weight: normal;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.title("Market Basket Analysis")

# VIEW
st.title("Market Basket Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="card">
            <div class="card-number">{trx_count}</div>
            <div class="card-label">TOTAL TRANSACTION</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="card">
            <div class="card-number">{trx_count}</div>
            <div class="card-label">TOTAL DATA</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="card">
            <div class="card-number">{item_count}</div>
            <div class="card-label">TOTAL ITEM</div>
        </div>
    """, unsafe_allow_html=True)


# Tampilkan judul
st.subheader("5 Produk dengan Jumlah Transaksi Tertinggi")
st.bar_chart(top_5_chart)