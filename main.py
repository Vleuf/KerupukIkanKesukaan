import csv
import os
from datetime import datetime
from collections import defaultdict

DATA_FILE = "data.csv"
STOCK_FILE = "stock.csv"

# =========================
# INIT FILE
# =========================
def init_files():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "No", "Tanggal", "Jam", "Produk",
                "Harga", "Jumlah", "Total",
                "Jenis", "Penanggung Jawab"
            ])

    if not os.path.exists(STOCK_FILE):
        with open(STOCK_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Produk", "Stock"])

# =========================
# STOCK MANAGEMENT
# =========================
def get_stock():
    stock = {}
    with open(STOCK_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            stock[row["Produk"]] = int(row["Stock"])
    return stock

def update_stock(product, quantity, jenis):
    stock = get_stock()

    if product not in stock:
        stock[product] = 0

    if jenis == "masuk":
        stock[product] += quantity
    elif jenis == "keluar":
        stock[product] -= quantity

    with open(STOCK_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Produk", "Stock"])
        for p, s in stock.items():
            writer.writerow([p, s])

# =========================
# ADD TRANSACTION
# =========================
def add_transaction():
    produk = input("Nama produk: ")
    harga = int(input("Harga per item: "))
    jumlah = int(input("Jumlah: "))
    jenis = input("Jenis (masuk/keluar): ").lower()
    penanggung = input("Nama penanggung jawab: ")

    total = harga * jumlah
    now = datetime.now()

    tanggal = now.strftime("%Y-%m-%d")
    jam = now.strftime("%H:%M:%S")

    # Hitung nomor
    with open(DATA_FILE, mode='r') as file:
        reader = list(csv.reader(file))
        no = len(reader)

    # Simpan data
    with open(DATA_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            no, tanggal, jam, produk,
            harga, jumlah, total,
            jenis, penanggung
        ])

    # Update stok
    update_stock(produk, jumlah, jenis)

    print("✅ Transaksi berhasil ditambahkan!")

# =========================
# SHOW DATA
# =========================
def show_data():
    with open(DATA_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)

# =========================
# REKAP BULANAN
# =========================
def monthly_report():
    laporan = defaultdict(int)

    with open(DATA_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            bulan = row["Tanggal"][:7]  # YYYY-MM
            total = int(row["Total"])

            if row["Jenis"] == "masuk":
                laporan[bulan] += total
            else:
                laporan[bulan] -= total

    print("\n📊 Rekap Bulanan:")
    for bulan, total in laporan.items():
        print(f"{bulan} : Rp {total}")

# =========================
# SHOW STOCK
# =========================
def show_stock():
    print("\n📦 Stock Produk:")
    stock = get_stock()
    for produk, jumlah in stock.items():
        print(f"{produk} : {jumlah}")

# =========================
# MAIN MENU
# =========================
def main():
    init_files()

    while True:
        print("\n=== MENU ===")
        print("1. Tambah Transaksi")
        print("2. Lihat Data")
        print("3. Rekap Bulanan")
        print("4. Lihat Stock")
        print("5. Keluar")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            add_transaction()
        elif pilihan == "2":
            show_data()
        elif pilihan == "3":
            monthly_report()
        elif pilihan == "4":
            show_stock()
        elif pilihan == "5":
            break
        else:
            print("❌ Pilihan tidak valid")

if __name__ == "__main__":
    main()
