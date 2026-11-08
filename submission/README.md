# Proyek Analisis Data: Air Quality Dataset (PRSA Beijing)

Analisis kualitas udara (fokus PM2.5) dari 12 stasiun pemantau di Beijing, 1 Maret 2013 – 28 Februari 2017.

## Pertanyaan Bisnis
1. Stasiun mana yang memiliki rata-rata PM2.5 tertinggi/terendah dan berapa persen hari yang melampaui 75 µg/m³?
2. Pada bulan dan jam berapa PM2.5 tertinggi/terendah (2014–2016) dan bagaimana tren tahunannya?
3. Variabel cuaca apa yang paling berkorelasi dengan PM2.5 dan dari arah angin mana PM2.5 tertinggi?

Analisis lanjutan: *binning* kategori kualitas udara, *manual grouping* klaster risiko stasiun dan musim, serta heatmap stasiun x bulan.

## Struktur Direktori
```
submission
├───dashboard
│   ├───main_data.csv          # data harian bersih per stasiun
│   ├───hourly_pattern.csv     # rata-rata PM2.5 per stasiun/tahun/bulan/jam
│   └───dashboard.py           # aplikasi Streamlit
├───data                       # 12 file CSV asli (satu per stasiun)
├───notebook.ipynb             # proses analisis lengkap (sudah dijalankan)
├───README.md
├───requirements.txt
└───url.txt                    # tautan dashboard Streamlit Cloud
```

## Setup Environment
```
python -m venv .venv
# Windows: .venv\Scripts\activate    |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan Notebook
Buka `notebook.ipynb` dengan Jupyter/VS Code/Google Colab dan jalankan seluruh sel dari atas ke bawah.
Notebook membaca file dari folder `data/` dan menulis ulang `dashboard/main_data.csv` serta `dashboard/hourly_pattern.csv`.
Jika memakai Google Colab, unggah folder `data/` ke direktori kerja Colab terlebih dahulu.

## Menjalankan Dashboard
Dari folder utama proyek (`submission`):
```
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`.

## Deploy ke Streamlit Community Cloud
1. Unggah folder proyek ke repository GitHub.
2. Masuk ke https://share.streamlit.io, pilih **New app**, pilih repository tersebut.
3. Isi **Main file path** dengan `dashboard/dashboard.py`, lalu **Deploy**.
4. Salin tautan aplikasi ke `url.txt`.
