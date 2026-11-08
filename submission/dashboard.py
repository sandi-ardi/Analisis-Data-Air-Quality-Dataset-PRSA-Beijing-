import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# ---------------------------------------------------------------------------
# Konfigurasi halaman & konstanta
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Dashboard Kualitas Udara Beijing", page_icon="🌫️", layout="wide")
sns.set_theme(style="whitegrid")

C_HIGH, C_LOW, C_NEUTRAL = "#C0392B", "#1B7F8C", "#B8BEC6"
BATAS_HARIAN = 75    # µg/m³ (rata-rata 24 jam, standar China Grade II)
BATAS_TAHUNAN = 35   # µg/m³ (rata-rata tahunan, standar China Grade II)
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
BINS_AQI = [0, 35, 75, 115, 150, 250, np.inf]
LABELS_AQI = ["Sangat baik (≤35)", "Baik (35–75)", "Polusi ringan (75–115)",
              "Polusi sedang (115–150)", "Polusi berat (150–250)", "Polusi parah (>250)"]
PALET_AQI = ["#2E8B57", "#8FBC5A", "#F4D03F", "#E67E22", "#C0392B", "#6C3483"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data
def load_daily():
    df = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"), parse_dates=["date"])
    return df


@st.cache_data
def load_hourly():
    return pd.read_csv(os.path.join(BASE_DIR, "hourly_pattern.csv"))


daily = load_daily()
hourly = load_hourly()

# ---------------------------------------------------------------------------
# Sidebar (filter)
# ---------------------------------------------------------------------------
st.sidebar.header("Filter Data")
all_stations = sorted(daily["station"].unique())
selected_stations = st.sidebar.multiselect("Stasiun", all_stations, default=all_stations)
year_min, year_max = int(daily["year"].min()), int(daily["year"].max())
year_range = st.sidebar.slider("Rentang tahun", year_min, year_max, (2014, 2016))
st.sidebar.caption(
    "Data mencakup 1 Mar 2013 – 28 Feb 2017. Tahun 2013 dan 2017 tidak penuh, "
    "sehingga pola bulanan paling akurat pada 2014–2016."
)

if not selected_stations:
    st.warning("Pilih minimal satu stasiun pada sidebar.")
    st.stop()

mask = (
    daily["station"].isin(selected_stations)
    & daily["year"].between(year_range[0], year_range[1])
)
df = daily[mask].dropna(subset=["PM2.5"]).copy()
df["melampaui"] = df["PM2.5"] > BATAS_HARIAN
df["kategori"] = pd.cut(df["PM2.5"], bins=BINS_AQI, labels=LABELS_AQI, include_lowest=True)

hr = hourly[
    hourly["station"].isin(selected_stations)
    & hourly["year"].between(year_range[0], year_range[1])
]

if df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# ---------------------------------------------------------------------------
# Header & KPI
# ---------------------------------------------------------------------------
st.title("🌫️ Dashboard Kualitas Udara Beijing (PM2.5)")
st.markdown(
    "Analisis data 12 stasiun pemantau kualitas udara Beijing (Mar 2013 – Feb 2017). "
    f"Ambang batas harian PM2.5 = **{BATAS_HARIAN} µg/m³** dan batas tahunan = **{BATAS_TAHUNAN} µg/m³** "
    "(standar kualitas udara China, Grade II)."
)

station_mean = df.groupby("station")["PM2.5"].mean().sort_values(ascending=False)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rata-rata PM2.5", f"{df['PM2.5'].mean():.1f} µg/m³")
col2.metric(f"Hari > {BATAS_HARIAN} µg/m³", f"{df['melampaui'].mean() * 100:.1f}%")
col3.metric("Stasiun tertinggi", station_mean.index[0], f"{station_mean.iloc[0]:.1f} µg/m³", delta_color="inverse")
col4.metric("Stasiun terendah", station_mean.index[-1], f"{station_mean.iloc[-1]:.1f} µg/m³", delta_color="off")

tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Per Stasiun", "2️⃣ Pola Waktu", "3️⃣ Cuaca & Arah Angin", "🔎 Analisis Lanjutan"
])


def clean_axes(ax, grid_axis="y"):
    ax.grid(axis=grid_axis, visible=False)
    sns.despine(ax=ax)


# ---------------------------------------------------------------------------
# Tab 1: Pertanyaan 1
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("Stasiun mana yang paling tercemar PM2.5?")
    stats = df.groupby("station").agg(
        mean_pm25=("PM2.5", "mean"),
        persen_melampaui=("melampaui", lambda s: s.mean() * 100),
    ).sort_values("mean_pm25", ascending=True)
    n = len(stats)
    if n >= 6:
        colors = [C_LOW if i < 3 else (C_HIGH if i >= n - 3 else C_NEUTRAL) for i in range(n)]
    else:
        colors = [C_NEUTRAL] * n

    fig, axes = plt.subplots(1, 2, figsize=(14, max(3.5, 0.55 * n + 1.5)), sharey=True)
    axes[0].barh(stats.index, stats["mean_pm25"], color=colors)
    for y, v in enumerate(stats["mean_pm25"]):
        axes[0].text(v + 1, y, f"{v:.1f}", va="center", fontsize=10)
    axes[0].axvline(BATAS_TAHUNAN, color="black", linestyle="--", linewidth=1)
    axes[0].set_title("Rata-rata PM2.5 (µg/m³)", loc="left", fontweight="bold")
    axes[0].set_xlim(0, max(100, stats["mean_pm25"].max() * 1.15))
    axes[1].barh(stats.index, stats["persen_melampaui"], color=colors)
    for y, v in enumerate(stats["persen_melampaui"]):
        axes[1].text(v + 0.6, y, f"{v:.1f}%", va="center", fontsize=10)
    axes[1].set_title(f"Hari melampaui {BATAS_HARIAN} µg/m³ (%)", loc="left", fontweight="bold")
    axes[1].set_xlim(0, max(55, stats["persen_melampaui"].max() * 1.15))
    for a in axes:
        clean_axes(a)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Garis putus-putus = batas tahunan 35 µg/m³. Merah = 3 stasiun tertinggi, teal = 3 stasiun terendah.")
    st.info(
        "**Insight:** Stasiun pusat/barat kota (mis. Dongsi, Nongzhanguan, Wanshouxigong) cenderung paling tercemar, "
        "sedangkan stasiun pinggiran (Dingling, Huairou, Changping) paling bersih. "
        "Seluruh stasiun berada jauh di atas batas tahunan."
    )

# ---------------------------------------------------------------------------
# Tab 2: Pertanyaan 2
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("Kapan PM2.5 mencapai puncak?")

    monthly = df.groupby("month")["PM2.5"].mean().reindex(range(1, 13))
    rank = monthly.rank(ascending=False)
    colors_m = [C_HIGH if r <= 3 else (C_LOW if r >= 10 else C_NEUTRAL) for r in rank]
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.bar(BULAN, monthly.values, color=colors_m)
    for x, v in enumerate(monthly.values):
        if not np.isnan(v):
            ax.text(x, v + 1.5, f"{v:.0f}", ha="center", fontsize=10)
    ax.set_ylabel("PM2.5 rata-rata (µg/m³)")
    ax.set_title("Rata-rata PM2.5 per bulan", loc="left", fontweight="bold")
    clean_axes(ax, "x")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    c1, c2 = st.columns([1.6, 1])
    with c1:
        hourly_mean = hr.groupby("hour")["PM2.5"].mean()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(hourly_mean.index, hourly_mean.values, color="#34495E", linewidth=2.5)
        ax.scatter([hourly_mean.idxmax()], [hourly_mean.max()], color=C_HIGH, s=80, zorder=3)
        ax.scatter([hourly_mean.idxmin()], [hourly_mean.min()], color=C_LOW, s=80, zorder=3)
        ax.annotate(f"Puncak {hourly_mean.idxmax():02d}:00 ({hourly_mean.max():.1f})",
                    (hourly_mean.idxmax(), hourly_mean.max()), xytext=(-110, 8),
                    textcoords="offset points", color=C_HIGH, fontsize=9, fontweight="bold")
        ax.annotate(f"Terendah {hourly_mean.idxmin():02d}:00 ({hourly_mean.min():.1f})",
                    (hourly_mean.idxmin(), hourly_mean.min()), xytext=(-5, -22),
                    textcoords="offset points", color=C_LOW, fontsize=9, fontweight="bold")
        ax.set_xticks(range(0, 24, 2))
        ax.set_xlabel("Jam dalam sehari")
        ax.set_ylabel("PM2.5 rata-rata (µg/m³)")
        ax.set_title("Pola per jam", loc="left", fontweight="bold")
        clean_axes(ax, "x")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with c2:
        yearly = df.groupby("year")["PM2.5"].mean()
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(yearly.index.astype(str), yearly.values, color=C_NEUTRAL, width=0.55)
        for x, v in enumerate(yearly.values):
            ax.text(x, v + 1.5, f"{v:.1f}", ha="center", fontsize=10, fontweight="bold")
        ax.set_ylim(0, max(100, yearly.max() * 1.15))
        ax.set_ylabel("PM2.5 rata-rata (µg/m³)")
        ax.set_title("Rata-rata tahunan", loc="left", fontweight="bold")
        clean_axes(ax, "x")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.info(
        "**Insight:** PM2.5 tertinggi pada musim dingin (Des, Nov, Feb) dan terendah pada musim panas (Agu). "
        "Dalam sehari, puncaknya pada malam hari (sekitar pukul 22:00). "
        "Pada 2014–2016, rata-rata tahunan turun sekitar 17%."
    )
    st.caption("Tahun 2013 (mulai Maret) dan 2017 (sampai Februari) tidak penuh, sehingga dapat membiaskan pola bulanan.")

# ---------------------------------------------------------------------------
# Tab 3: Pertanyaan 3
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("Faktor cuaca apa yang paling berpengaruh pada PM2.5?")
    nama_cuaca = {"WSPM": "Kecepatan angin", "TEMP": "Suhu", "RAIN": "Curah hujan",
                  "PRES": "Tekanan udara", "DEWP": "Titik embun"}
    corr = df[["PM2.5"] + list(nama_cuaca)].corr()["PM2.5"].drop("PM2.5")
    corr = corr.reindex(corr.abs().sort_values(ascending=True).index)

    c1, c2 = st.columns(2)
    with c1:
        fig, ax = plt.subplots(figsize=(7, 4.2))
        cols = [C_HIGH if abs(v) == corr.abs().max() else C_NEUTRAL for v in corr.values]
        ax.barh([nama_cuaca[i] for i in corr.index], corr.values, color=cols)
        for y, v in enumerate(corr.values):
            ax.text(v + (0.01 if v >= 0 else -0.01), y, f"{v:.2f}", va="center",
                    ha="left" if v >= 0 else "right", fontsize=10)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlim(-0.55, 0.3)
        ax.set_xlabel("Korelasi Pearson dengan PM2.5")
        ax.set_title("Korelasi variabel cuaca", loc="left", fontweight="bold")
        clean_axes(ax, "y")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with c2:
        wdf = df.dropna(subset=["WSPM"]).copy()
        wdf["kelas"] = pd.cut(wdf["WSPM"], bins=[0, 1, 2, 3, np.inf],
                              labels=["≤ 1 m/s", "1–2 m/s", "2–3 m/s", "> 3 m/s"], include_lowest=True)
        ws = wdf.groupby("kelas", observed=True)["PM2.5"].mean()
        fig, ax = plt.subplots(figsize=(7, 4.2))
        ax.bar(ws.index.astype(str), ws.values, color=C_NEUTRAL, width=0.6)
        for x, v in enumerate(ws.values):
            ax.text(x, v + 2, f"{v:.0f}", ha="center", fontsize=11, fontweight="bold")
        ax.set_ylabel("PM2.5 rata-rata (µg/m³)")
        ax.set_xlabel("Kecepatan angin harian")
        ax.set_title("PM2.5 menurut kecepatan angin", loc="left", fontweight="bold")
        clean_axes(ax, "x")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    wd = df.dropna(subset=["wd"]).groupby("wd")["PM2.5"].mean().sort_values(ascending=True)
    n = len(wd)
    cols = [C_LOW if i < 3 else (C_HIGH if i >= n - 3 else C_NEUTRAL) for i in range(n)]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.barh(wd.index, wd.values, color=cols)
    for y, v in enumerate(wd.values):
        ax.text(v + 1, y, f"{v:.0f}", va="center", fontsize=10)
    ax.set_xlabel("PM2.5 rata-rata (µg/m³)")
    ax.set_title("PM2.5 menurut arah angin dominan harian", loc="left", fontweight="bold")
    clean_axes(ax, "y")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.info(
        "**Insight:** Kecepatan angin berkorelasi negatif paling kuat dengan PM2.5. "
        "Angin lemah (≤ 1 m/s) membuat PM2.5 tertahan, dan angin dari arah timur membawa PM2.5 tertinggi, "
        "sedangkan angin barat laut paling bersih. Korelasi tidak membuktikan sebab-akibat."
    )

# ---------------------------------------------------------------------------
# Tab 4: Analisis lanjutan (binning & manual grouping)
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("Binning kategori kualitas udara & klaster risiko stasiun")
    st.markdown(
        "**Teknik:** *binning* (`pd.cut`) rata-rata PM2.5 harian ke 6 kategori (batas indeks kualitas udara China) "
        "dan *manual grouping* stasiun menjadi 3 klaster risiko (rendah < 75, sedang 75–85, tinggi ≥ 85 µg/m³)."
    )
    kat = (pd.crosstab(df["station"], df["kategori"], normalize="index") * 100).reindex(columns=LABELS_AQI, fill_value=0)
    kat["tidak_sehat"] = kat[LABELS_AQI[2:]].sum(axis=1)
    kat = kat.sort_values("tidak_sehat", ascending=True).drop(columns="tidak_sehat")

    fig, ax = plt.subplots(figsize=(12, max(3.5, 0.5 * len(kat) + 2)))
    left = np.zeros(len(kat))
    for lab, col in zip(LABELS_AQI, PALET_AQI):
        vals = kat[lab].values
        ax.barh(kat.index, vals, left=left, color=col, label=lab, edgecolor="white", linewidth=0.5)
        for y, (l, v) in enumerate(zip(left, vals)):
            if v >= 6:
                ax.text(l + v / 2, y, f"{v:.0f}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        left += vals
    ax.set_xlim(0, 100)
    ax.set_xlabel("% hari")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.15), frameon=False, fontsize=9)
    clean_axes(ax, "y")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("**Klaster risiko stasiun** (berdasarkan rata-rata PM2.5 pada filter yang dipilih)")
    cl = df.groupby("station").agg(
        rata_rata_pm25=("PM2.5", "mean"),
        persen_hari_melampaui=("melampaui", lambda s: s.mean() * 100),
    )
    cl["klaster_risiko"] = pd.cut(cl["rata_rata_pm25"], bins=[0, 75, 85, np.inf],
                                  labels=["Risiko rendah (<75)", "Risiko sedang (75–85)", "Risiko tinggi (≥85)"],
                                  right=False)
    st.dataframe(cl.sort_values("rata_rata_pm25", ascending=False).round(1), use_container_width=True)

    st.markdown("**Heatmap rata-rata PM2.5: stasiun x bulan**")
    heat = df.pivot_table(index="station", columns="month", values="PM2.5", aggfunc="mean")
    heat = heat.reindex(columns=range(1, 13))
    heat.columns = BULAN
    heat = heat.loc[heat.mean(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(12, max(3.5, 0.45 * len(heat) + 1.5)))
    sns.heatmap(heat, cmap="YlOrRd", annot=True, fmt=".0f", linewidths=0.5,
                cbar_kws={"label": "PM2.5 (µg/m³)"}, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("### Rekomendasi")
    st.markdown(
        "- Prioritaskan pengendalian emisi di wilayah pusat/barat kota (klaster risiko tinggi–sedang).\n"
        "- Terapkan pembatasan emisi musiman pada **November–Februari**, fokus Desember.\n"
        "- Aktifkan peringatan dini saat angin lemah (≤ 1 m/s), terutama dari arah timur.\n"
        "- Pertahankan kebijakan yang menurunkan PM2.5 sejak 2014 dan tetapkan target menuju 35 µg/m³."
    )

st.caption("Sumber data: Beijing Multi-Site Air-Quality Data (PRSA), 12 stasiun, 2013–2017.")
