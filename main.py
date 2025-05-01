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


df_sorted['year_month'] = df_sorted['date'].dt.to_period('M')

# Dictionary untuk menyimpan hasil
item_counts = {}

# Looping setiap baris untuk menghitung kemunculan item
for index, row in df_sorted.iterrows():
    year_month = row['year_month']
    items = row['nama_barang'].split(', ')  # Pisahkan item jika lebih dari satu

    for item in items:
        key = (year_month, item)  # Gabungan Tahun-Bulan dan Item sebagai kunci
        item_counts[key] = item_counts.get(key, 0) + 1  # Tambah jumlah kemunculan

# Ubah hasil ke DataFrame
result_df = pd.DataFrame([(ym, item, count) for (ym, item), count in item_counts.items()],
                         columns=['year_month', 'nama_barang', 'total_kemunculan'])

# Urutkan berdasarkan Tahun-Bulan dan total kemunculan terbesar
result_df = result_df.sort_values(by=['year_month', 'total_kemunculan'], ascending=[True, False])


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
st.markdown(
    """
    <div style="margin-top: 50px;">
    </div>
    """,
    unsafe_allow_html=True
)
st.subheader("5 Produk dengan Jumlah Transaksi Tertinggi")
st.bar_chart(top_5_chart)


# SELECT TOP TRXs PER MONTH
# Ambil 5 item terbanyak di setiap bulan
top_trxs_per_month = result_df.groupby('year_month').apply(lambda x: x.nlargest(5, 'total_kemunculan')).reset_index(drop=True)
months = []

for month in top_trxs_per_month['year_month'].unique():
    months.append(month)

def getTopTrxPerMonth(month):
    subset = top_trxs_per_month[top_trxs_per_month['year_month'] == month]
    st.bar_chart(subset, x='nama_barang', x_label="Nama Barang", y='total_kemunculan', y_label="Jumlah Kemunculan", horizontal=True)
    return month

st.markdown(
    """
    <div style="margin-top: 50px;">
    </div>
    """,
    unsafe_allow_html=True
)
st.subheader("5 Produk dengan Jumlah Transaksi Tertinggi Per Bulan")
topTrxPerMonthOptions = st.selectbox(
    "Pilih bulan:",
    months,
    key="topTrx"
)

st.write(getTopTrxPerMonth(topTrxPerMonthOptions))
# END SELECT TOP TRXs PER MONTH

# SELECT TOP SALES PER MONTH
# Ambil format tahun-bulan
df_sorted["tahun_bulan"] = df_sorted["date"].dt.to_period("M").astype(str)
# Hitung jumlah pcs per tahun-bulan dan nama_barang
monthly_sales = df_sorted.groupby(["tahun_bulan", "nama_barang"]).agg({"pcs": "sum"}).reset_index()
# Sortir data berdasarkan tahun-bulan dan jumlah pcs yang terjual
monthly_sales = monthly_sales.sort_values(by=["tahun_bulan", "pcs"], ascending=[True, False])
# Ambil 5 item terbanyak di setiap bulan
top_saless_per_month = monthly_sales.groupby('tahun_bulan').apply(lambda x: x.nlargest(5, 'pcs')).reset_index(drop=True)

topSalesMonths = []

for month in top_saless_per_month['tahun_bulan'].unique():
    topSalesMonths.append(month)

def getTopSalesPerMonth(month):
    subset = top_saless_per_month[top_saless_per_month['tahun_bulan'] == month]
    st.bar_chart(subset, x='nama_barang', x_label="Nama Barang", y='pcs', y_label="Jumlah Kemunculan", horizontal=True)
    return month

st.subheader("5 Produk dengan Jumlah Penjualan Tertinggi Per Bulan")
topSalesPerMonthOptions = st.selectbox(
    "Pilih bulan:",
    topSalesMonths,
    key="topSales"
)

st.write(getTopSalesPerMonth(topSalesPerMonthOptions))
# END SELECT TOP SALES PER MONTH