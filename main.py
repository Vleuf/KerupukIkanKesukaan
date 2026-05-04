import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================
# CONFIG
# =========================
DATA_FILE = "data.csv"
STOCK_FILE = "stock.csv"

st.set_page_config(page_title="Finance App", layout="wide")
st.title("📊 Sistem Pemasukan & Pengeluaran + Stock")

# =========================
# INIT FILE
# =========================
def init_file():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "No","Tanggal","Jam","Produk",
            "Harga","Jumlah","Total",
            "Jenis","Penanggung Jawab"
        ])
        df.to_csv(DATA_FILE, index=False)

    if not os.path.exists(STOCK_FILE):
        df = pd.DataFrame(columns=["Produk","Stock"])
        df.to_csv(STOCK_FILE, index=False)

# =========================
# LOAD DATA
def edit_data(no_edit, produk, harga, jumlah, jenis, pj):
    df = load_data()
    stock = load_stock()

    # cari index berdasarkan nomor
    idx = df[df["No"] == no_edit].index

    if len(idx) == 0:
        return False

    idx = idx[0]

    # === rollback stock lama ===
    old_produk = df.at[idx, "Produk"]
    old_jumlah = df.at[idx, "Jumlah"]
    old_jenis = df.at[idx, "Jenis"]

    if old_produk in stock["Produk"].values:
        s_idx = stock[stock["Produk"] == old_produk].index[0]

        if old_jenis == "masuk":
            stock.at[s_idx, "Stock"] -= old_jumlah
        else:
            stock.at[s_idx, "Stock"] += old_jumlah

    # === update data baru ===
    total = harga * jumlah

    df.at[idx, "Produk"] = produk
    df.at[idx, "Harga"] = harga
    df.at[idx, "Jumlah"] = jumlah
    df.at[idx, "Total"] = total
    df.at[idx, "Jenis"] = jenis
    df.at[idx, "Penanggung Jawab"] = pj

    # === update stock baru ===
    if produk in stock["Produk"].values:
        s_idx = stock[stock["Produk"] == produk].index[0]

        if jenis == "masuk":
            stock.at[s_idx, "Stock"] += jumlah
        else:
            stock.at[s_idx, "Stock"] -= jumlah
    else:
        new_stock = jumlah if jenis == "masuk" else -jumlah
        stock.loc[len(stock)] = [produk, new_stock]

    # simpan
    df.to_csv(DATA_FILE, index=False)
    stock.to_csv(STOCK_FILE, index=False)

    return True
# =========================
def load_data():
    return pd.read_csv(DATA_FILE)

def load_stock():
    return pd.read_csv(STOCK_FILE)

# =========================
# UPDATE STOCK
# =========================
def update_stock(produk, jumlah, jenis):
    stock = load_stock()

    if produk in stock["Produk"].values:
        idx = stock[stock["Produk"] == produk].index[0]

        if jenis == "masuk":
            stock.at[idx, "Stock"] += jumlah
        else:
            stock.at[idx, "Stock"] -= jumlah
    else:
        new_stock = jumlah if jenis == "masuk" else -jumlah
        stock.loc[len(stock)] = [produk, new_stock]

    stock.to_csv(STOCK_FILE, index=False)

# =========================
# TAMBAH DATA
# =========================
def tambah_data(produk, harga, jumlah, jenis, pj):
    df = load_data()

    no = len(df) + 1
    now = datetime.now()

    tanggal = now.strftime("%Y-%m-%d")
    jam = now.strftime("%H:%M:%S")
    total = harga * jumlah

    new_row = {
        "No": no,
        "Tanggal": tanggal,
        "Jam": jam,
        "Produk": produk,
        "Harga": harga,
        "Jumlah": jumlah,
        "Total": total,
        "Jenis": jenis,
        "Penanggung Jawab": pj
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    update_stock(produk, jumlah, jenis)

# =========================
# INIT
# =========================
init_file()

# =========================
# SIDEBAR MENU
# =========================
menu = st.sidebar.selectbox("Menu", [
    "Input Transaksi",
    "Data Transaksi",
    "Stock Produk",
    "Rekap Bulanan"
])

# =========================
# INPUT TRANSAKSI
# =========================
if menu == "Input Transaksi":
    st.subheader("➕ Tambah Transaksi")

    col1, col2 = st.columns(2)

    with col1:
        produk = st.text_input("Nama Produk")
        harga = st.number_input("Harga per Item", min_value=0)

    with col2:
        jumlah = st.number_input("Jumlah", min_value=1)
        jenis = st.selectbox("Jenis", ["masuk", "keluar"])

    pj = st.text_input("Penanggung Jawab")

    if st.button("Simpan Transaksi"):
        if produk == "" or pj == "":
            st.warning("Harap isi semua data!")
        else:
            tambah_data(produk, harga, jumlah, jenis, pj)
            st.success("✅ Data berhasil disimpan!")

# =========================
# DATA TRANSAKSI
# =========================
elif menu == "Data Transaksi":
    st.subheader("📋 Data Transaksi")

    df = load_data()
    st.dataframe(df, use_container_width=True)

# =========================
# STOCK
# =========================
elif menu == "Stock Produk":
    st.subheader("📦 Stock Produk")

    stock = load_stock()
    st.dataframe(stock, use_container_width=True)

# =========================
# REKAP BULANAN
# =========================
elif menu == "Rekap Bulanan":
    st.subheader("📈 Rekap Bulanan")

    df = load_data()

    if len(df) == 0:
        st.info("Belum ada data")
    else:
        df["Bulan"] = df["Tanggal"].astype(str).str[:7]

        summary = df.groupby(["Bulan","Jenis"])["Total"].sum().unstack().fillna(0)

        if "masuk" not in summary:
            summary["masuk"] = 0
        if "keluar" not in summary:
            summary["keluar"] = 0

        summary["Saldo"] = summary["masuk"] - summary["keluar"]

        st.dataframe(summary, use_container_width=True)

        st.subheader("📊 Grafik")
        st.bar_chart(summary[["masuk","keluar"]])
