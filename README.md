# 🌫️ Analisis Kualitas Udara Beijing (PM2.5)

Proyek analisis data end-to-end atas **Beijing Multi-Site Air Quality Dataset (PRSA)**: 12 stasiun pemantauan,
420.768 pengamatan per jam, 1 Maret 2013 – 28 Februari 2017. Mencakup data wrangling, EDA, visualisasi,
analisis lanjutan, dan dashboard interaktif.

🔗 **Demo dashboard:** <URL_STREAMLIT_ANDA>

## Pertanyaan Bisnis
- **Pertanyaan 1:** Stasiun pemantauan mana (dari 12 stasiun) yang memiliki rata-rata konsentrasi PM2.5 tertinggi dan terendah, serta berapa persen hari di setiap stasiun yang melampaui ambang batas harian standar kualitas udara China (75 µg/m³) selama periode 1 Maret 2013 – 28 Februari 2017?
- **Pertanyaan 2:** Pada bulan dan jam berapa rata-rata konsentrasi PM2.5 mencapai titik tertinggi dan terendah sepanjang tiga tahun kalender penuh 2014–2016, dan seberapa besar perubahan rata-rata tahunannya dari 2014 ke 2016?
- **Pertanyaan 3:** Dari variabel cuaca (suhu, tekanan udara, titik embun, curah hujan, kecepatan angin), variabel mana yang memiliki korelasi paling kuat dengan PM2.5 harian, dan dari arah angin mana PM2.5 rata-rata paling tinggi, selama periode 1 Maret 2013 – 28 Februari 2017?

## Temuan Utama
- **Wanshouxigong** tertinggi (≈84,5 µg/m³) dan **Dingling** terendah (≈62,5 µg/m³). Sembilan stasiun urban hampir setara,
  dengan 40–42,5% hari melampaui 75 µg/m³.
- PM2.5 musim dingin **≈52% lebih tinggi** dari musim panas (rata-rata), puncak di **Desember**. Berdasarkan median selisihnya
  hanya ≈10%, sehingga lonjakan musim dingin terutama didorong episode polusi ekstrem.
- Angin lemah (<1 m/s) berkaitan dengan PM2.5 ≈100 µg/m³, dibanding ≈25 µg/m³ saat angin >5 m/s.

## Proses & Teknik
- **Data wrangling:** interpolasi missing value (celah ≤6 jam), perbaikan nilai tidak valid (PM2.5 > PM10),
  penanganan outlier berbasis analisis (episode smog nyata dipertahankan).
- **Analisis:** agregasi per stasiun/musim/jam, binning kategori AQI China, korelasi, dan binning kecepatan angin.
- **Visualisasi:** matplotlib & seaborn dengan palet ramah buta warna dan prinsip integritas data.
- **Dashboard:** Streamlit dengan filter rentang tanggal dan stasiun.

## Tech Stack
Python · pandas · NumPy · matplotlib · seaborn · Streamlit · Jupyter Notebook

## Cara Menjalankan
    pip install -r requirements.txt
    streamlit run dashboard/dashboard.py

Detail setup lengkap ada di bagian bawah README ini.

## Rekomendasi
Prioritaskan pengendalian emisi di area urban, jadwalkan intervensi dan peringatan dini Oktober–Februari,
dan gunakan prakiraan angin lemah sebagai pemicu peringatan dini.

## Sumber Data
Beijing Multi-Site Air Quality Data (PRSA), Chen, S. (2017), UCI Machine Learning Repository.
