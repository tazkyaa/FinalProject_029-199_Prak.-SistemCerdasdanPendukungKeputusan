import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SPK Pemilihan Diet – Weighted Product",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global Style ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Font base */
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

    /* Header utama */
    .page-header {
        background: linear-gradient(120deg, #1b5e20, #388e3c);
        color: white;
        padding: 28px 36px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .page-header h1 {
        margin: 0 0 6px 0;
        font-size: 1.75rem;
        font-weight: 700;
        color: white;
    }
    .page-header p {
        margin: 0;
        font-size: 0.9rem;
        opacity: 0.85;
        color: white;
    }

    /* Section title */
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1b5e20;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        border-left: 4px solid #43a047;
        padding-left: 10px;
        margin: 20px 0 12px 0;
    }

    /* Kartu metrik kustom */
    .stat-card {
        background: #f9fafb;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .stat-card .val {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2e7d32;
    }
    .stat-card .lbl {
        font-size: 0.8rem;
        color: #777;
        margin-top: 2px;
    }

    /* Kartu kriteria */
    .krit-card {
        background: #fff;
        border: 1px solid #e8f5e9;
        border-left: 4px solid #43a047;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .krit-card .krit-name { font-weight: 600; font-size: 0.92rem; color: #212121; }
    .krit-card .krit-type-cost    { color: #b71c1c; font-size: 0.8rem; font-weight: 700; }
    .krit-card .krit-type-benefit { color: #1b5e20; font-size: 0.8rem; font-weight: 700; }
    .krit-card .krit-desc { font-size: 0.82rem; color: #333; margin-top: 2px; }

    /* Kartu hasil peringkat */
    .rank-card {
        border-radius: 10px;
        padding: 20px 16px;
        text-align: center;
        border: 1px solid #e0e0e0;
        height: 100%;
    }
    .rank-card .rank-num  { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #888; }
    .rank-card .rank-diet { font-size: 1.15rem; font-weight: 700; margin: 8px 0 4px 0; }
    .rank-card .rank-val  { font-size: 1rem; font-weight: 600; }
    .rank-card .rank-desc { font-size: 0.78rem; color: #666; margin-top: 8px; line-height: 1.4; }

    /* Box rekomendasi akhir */
    .result-box {
        background: #f1f8e9;
        border: 1.5px solid #66bb6a;
        border-radius: 10px;
        padding: 20px 24px;
        margin-top: 16px;
    }
    .result-box .result-label { font-size: 0.8rem; color: #555; text-transform: uppercase; letter-spacing: 0.07em; }
    .result-box .result-diet  { font-size: 1.4rem; font-weight: 700; color: #1b5e20; margin: 4px 0; }
    .result-box .result-desc  { font-size: 0.88rem; color: #444; }

    /* Sidebar */
    div[data-testid="stSidebar"] { background: #fafafa; }
    div[data-testid="stSidebar"] .stSlider label { font-size: 0.85rem !important; }

    /* Tab styling */
    button[data-baseweb="tab"] { font-size: 0.9rem !important; font-weight: 600 !important; }

    /* Hilangkan padding berlebih di atas */
    .block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ─── Konstanta ────────────────────────────────────────────────────────────────
KRITERIA  = [
    'BMI',
    'Daily_Caloric_Intake',
    'Weekly_Exercise_Hours',
    'Adherence_to_Diet_Plan',
    'Dietary_Nutrient_Imbalance_Score',
]
LABEL_K = [
    'BMI',
    'Kalori Harian (kkal)',
    'Olahraga Mingguan (jam)',
    'Kepatuhan Diet (%)',
    'Skor Imbalance Nutrisi',
]
TIPE      = ['cost', 'cost', 'benefit', 'benefit', 'cost']
DIET_LIST = ['Balanced', 'Low_Carb', 'Low_Sodium']
DIET_DESC = {
    'Balanced'  : 'Diet seimbang dengan proporsi karbohidrat, protein, dan lemak yang ideal. Cocok untuk menjaga berat badan dan kesehatan umum.',
    'Low_Carb'  : 'Diet rendah karbohidrat yang mendorong tubuh membakar lemak sebagai sumber energi utama. Efektif untuk penurunan berat badan.',
    'Low_Sodium': 'Diet rendah garam untuk mengontrol tekanan darah dan mengurangi retensi cairan dalam tubuh.',
}
DIET_COLOR = {'Balanced': '#43a047', 'Low_Carb': '#1e88e5', 'Low_Sodium': '#fb8c00'}
RANK_STYLE = [
    {'bg': '#fffde7', 'border': '#f9a825', 'label': 'Peringkat 1 — Rekomendasi Utama'},
    {'bg': '#fafafa', 'border': '#bdbdbd', 'label': 'Peringkat 2'},
    {'bg': '#fff3e0', 'border': '#ef6c00', 'label': 'Peringkat 3'},
]

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("diet_spk_clean.csv")

@st.cache_data
def get_profil(_df):
    return _df.groupby('Diet_Recommendation')[KRITERIA].mean()

df          = load_data()
profil_diet = get_profil(df)

# ─── WP Functions ─────────────────────────────────────────────────────────────
def norm_bobot(raw):
    w = np.array(raw, dtype=float)
    return w / w.sum()

def hitung_wp(nilai_pasien, profil, bobot, tipe):
    mat      = profil[KRITERIA].astype(float).copy()
    all_rows = np.vstack([mat.values, nilai_pasien])
    norm     = mat.copy()
    for j, k in enumerate(KRITERIA):
        col    = all_rows[:, j]
        mn, mx = col.min(), col.max()
        if mx == mn:
            norm[k] = 1.0
        elif tipe[j] == 'benefit':
            norm[k] = (mat[k] - mn) / (mx - mn)
        else:
            norm[k] = (mx - mat[k]) / (mx - mn)
    norm = norm.clip(lower=1e-9)
    S = np.ones(len(mat))
    for j, k in enumerate(KRITERIA):
        S *= norm[k].values ** bobot[j]
    V = S / S.sum()
    return {d: float(v) for d, v in zip(mat.index, V)}, norm, S, V

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Pengaturan Bobot Kriteria")
    st.caption("Geser slider untuk menyesuaikan kepentingan setiap kriteria. Bobot akan dinormalisasi otomatis sehingga totalnya selalu 1,0.")
    st.divider()

    raw_w    = []
    defaults = [5, 4, 7, 8, 6]
    for i, lbl in enumerate(LABEL_K):
        w = st.slider(lbl, min_value=1, max_value=10, value=defaults[i], key=f"wb{i}")
        raw_w.append(w)

    bobot = norm_bobot(raw_w)

    st.divider()
    st.markdown("**Bobot Ternormalisasi**")
    df_bw = pd.DataFrame({
        'Kriteria': [f'C{i+1} – {LABEL_K[i][:14]}' for i in range(5)],
        'Bobot (w)': bobot.round(4),
    })
    st.dataframe(df_bw, hide_index=True, use_container_width=True)
    st.caption(f"Total: {bobot.sum():.4f}")

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>Sistem Pendukung Keputusan Pemilihan Jenis Diet</h1>
    <p>Metode Weighted Product (WP) &nbsp;&middot;&nbsp; 250 Data Pasien &nbsp;&middot;&nbsp; 5 Kriteria &nbsp;&middot;&nbsp; 3 Alternatif Jenis Diet</p>
</div>
""", unsafe_allow_html=True)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_data, tab_spk, tab_viz, tab_profil = st.tabs(["Data", "Hitung SPK", "Visualisasi", "Profil Kelompok"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA
# ══════════════════════════════════════════════════════════════════════════════
with tab_data:

    # Stat cards
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (str(len(df)), "Total Pasien"),
        ("5", "Jumlah Kriteria"),
        ("3", "Alternatif Diet"),
        (str(len(df.columns)), "Jumlah Kolom"),
    ]
    for col, (val, lbl) in zip([c1, c2, c3, c4], stats):
        col.markdown(f'<div class="stat-card"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Dataset</div>', unsafe_allow_html=True)

    # Filter baris
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        fil_gender  = st.selectbox("Jenis Kelamin",
            ["Semua"] + sorted(df['Gender'].dropna().unique().tolist()))
    with fc2:
        fil_disease = st.selectbox("Tipe Penyakit",
            ["Semua"] + sorted(df['Disease_Type'].dropna().unique().tolist()))
    with fc3:
        fil_diet = st.selectbox("Rekomendasi Diet", ["Semua"] + DIET_LIST)

    df_show = df.copy()
    if fil_gender  != "Semua": df_show = df_show[df_show['Gender']              == fil_gender]
    if fil_disease != "Semua": df_show = df_show[df_show['Disease_Type']        == fil_disease]
    if fil_diet    != "Semua": df_show = df_show[df_show['Diet_Recommendation'] == fil_diet]

    cap_col, dl_col = st.columns([5, 1])
    with cap_col:
        st.caption(f"Menampilkan {len(df_show)} dari {len(df)} data. Klik header kolom untuk mengurutkan.")
    with dl_col:
        st.download_button("Download CSV", df_show.to_csv(index=False).encode(),
                           "diet_filtered.csv", "text/csv")

    st.dataframe(df_show, use_container_width=True, height=480)

    # Statistik & profil
    st.markdown('<div class="section-title">Statistik Kriteria</div>', unsafe_allow_html=True)
    sa, sb = st.columns([3, 2])
    with sa:
        st.caption("Statistik deskriptif 5 kriteria SPK")
        st.dataframe(df[KRITERIA].describe().T.round(3), use_container_width=True)
    with sb:
        st.caption("Profil rata-rata per jenis diet — nilai ini digunakan sebagai alternatif dalam perhitungan WP")
        pshow = profil_diet[KRITERIA].round(3).copy()
        pshow.columns = ['BMI', 'Kalori', 'Olahraga', 'Kepatuhan', 'Imbalance']
        st.dataframe(pshow, use_container_width=True)

    # Keterangan kriteria
    st.markdown('<div class="section-title">Keterangan Kriteria</div>', unsafe_allow_html=True)
    info_k = [
        ('BMI',                              'cost',    'C1', 'Indikator utama kelebihan berat badan. Nilai lebih rendah mencerminkan kondisi lebih baik.'),
        ('Daily_Caloric_Intake',             'cost',    'C2', 'Total asupan kalori harian (kkal). Kalori berlebih menghambat penurunan berat badan.'),
        ('Weekly_Exercise_Hours',            'benefit', 'C3', 'Total jam olahraga per minggu. Semakin tinggi, semakin efektif penurunan berat badan.'),
        ('Adherence_to_Diet_Plan',           'benefit', 'C4', 'Tingkat kepatuhan menjalani rencana diet (%). Semakin tinggi semakin baik.'),
        ('Dietary_Nutrient_Imbalance_Score', 'cost',    'C5', 'Skor ketidakseimbangan nutrisi (0–5). Mendekati 0 berarti nutrisi sangat seimbang.'),
    ]
    ka, kb = st.columns(2)
    for i, (name, tipe_val, kode, desc) in enumerate(info_k):
        tipe_html = (f'<span class="krit-type-benefit">Benefit (makin tinggi makin baik)</span>'
                     if tipe_val == 'benefit'
                     else f'<span class="krit-type-cost">Cost (makin rendah makin baik)</span>')
        html = f'<div class="krit-card"><div class="krit-name">{kode} &mdash; {name}</div>{tipe_html}<div class="krit-desc">{desc}</div></div>'
        if i % 2 == 0:
            ka.markdown(html, unsafe_allow_html=True)
        else:
            kb.markdown(html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — HITUNG SPK
# ══════════════════════════════════════════════════════════════════════════════
with tab_spk:
    st.markdown('<div class="section-title">Input Data Pasien</div>', unsafe_allow_html=True)
    st.caption("Masukkan data kondisi pasien, kemudian klik tombol Hitung untuk mendapatkan rekomendasi jenis diet.")

    ic1, ic2 = st.columns(2)
    with ic1:
        nama       = st.text_input("Nama Pasien", value="Pasien Baru")
        inp_bmi    = st.number_input("BMI", min_value=10.0, max_value=60.0, value=28.0, step=0.1,
                                     help="Normal: 18.5–24.9 | Overweight: 25–29.9 | Obesitas: ≥30")
        inp_kalori = st.number_input("Kalori Harian (kkal)", min_value=1000, max_value=5000,
                                     value=2400, step=50, help="Rata-rata dataset: ±2.446 kkal/hari")
    with ic2:
        inp_olahraga  = st.slider("Olahraga Mingguan (jam)",    0.0, 10.0, 4.0, 0.5)
        inp_kepatuhan = st.slider("Kepatuhan Diet (%)",         50.0, 100.0, 70.0, 0.5)
        inp_imbalance = st.slider("Skor Imbalance Nutrisi (0–5)", 0.0, 5.0, 2.5, 0.1,
                                  help="0 = nutrisi sangat seimbang | 5 = sangat tidak seimbang")

    nilai_pasien = np.array([inp_bmi, inp_kalori, inp_olahraga, inp_kepatuhan, inp_imbalance])

    st.markdown('<div class="section-title">Bobot Kriteria Aktif</div>', unsafe_allow_html=True)
    st.caption("Ubah bobot melalui panel di sebelah kiri.")
    df_bobot = pd.DataFrame({
        'Kode'               : [f'C{i+1}' for i in range(5)],
        'Kriteria'           : LABEL_K,
        'Jenis'              : TIPE,
        'Bobot Mentah'       : raw_w,
        'Bobot Ternormalisasi': bobot.round(4),
    })
    st.dataframe(df_bobot, use_container_width=True, hide_index=True)

    st.divider()
    col_b = st.columns([1, 2, 1])
    with col_b[1]:
        run = st.button("Hitung Rekomendasi Diet", type="primary", use_container_width=True)

    if run:
        hasil_v, tbl_norm, S_vals, V_vals = hitung_wp(nilai_pasien, profil_diet, bobot, TIPE)
        ranking = sorted(hasil_v.items(), key=lambda x: x[1], reverse=True)

        st.success(f"Perhitungan selesai untuk pasien: {nama}")

        # Tabel perangkingan
        st.markdown('<div class="section-title">Tabel Hasil Perangkingan</div>', unsafe_allow_html=True)
        df_rank = pd.DataFrame({
            'Peringkat'  : [1, 2, 3],
            'Jenis Diet' : [r[0] for r in ranking],
            'Nilai V'    : [round(r[1], 6) for r in ranking],
            'Persentase' : [f"{r[1]*100:.2f}%" for r in ranking],
            'Keterangan' : ['Rekomendasi utama', 'Alternatif 1', 'Alternatif 2'],
        })

        def hl(row):
            if row['Peringkat'] == 1: return ['background-color:#c8e6c9;color:#1b5e20;font-weight:600'] * len(row)
            if row['Peringkat'] == 2: return ['background-color:#bbdefb;color:#0d47a1;font-weight:600'] * len(row)
            return ['background-color:#ffe0b2;color:#e65100;font-weight:600'] * len(row)

        st.dataframe(df_rank.style.apply(hl, axis=1), use_container_width=True, hide_index=True)

        # Kartu peringkat
        st.markdown('<div class="section-title">Rincian Peringkat</div>', unsafe_allow_html=True)
        rc1, rc2, rc3 = st.columns(3)
        for i, (col_r, (diet, v)) in enumerate(zip([rc1, rc2, rc3], ranking)):
            st_r = RANK_STYLE[i]
            with col_r:
                st.markdown(f"""
                <div class="rank-card" style="background:{st_r['bg']};border-color:{st_r['border']};">
                    <div class="rank-num">{st_r['label']}</div>
                    <div class="rank-diet" style="color:{DIET_COLOR[diet]}">{diet}</div>
                    <div class="rank-val" style="color:{st_r['border']}">V = {v:.6f}</div>
                    <div class="rank-desc">{DIET_DESC[diet]}</div>
                </div>
                """, unsafe_allow_html=True)

        # Box rekomendasi
        best_diet, best_v = ranking[0]
        st.markdown(f"""
        <div class="result-box">
            <div class="result-label">Rekomendasi Diet untuk {nama}</div>
            <div class="result-diet">{best_diet}</div>
            <div class="result-desc">{DIET_DESC[best_diet]}</div>
        </div>
        """, unsafe_allow_html=True)

        # Detail perhitungan
        st.divider()
        with st.expander("Detail Langkah Perhitungan WP"):
            st.markdown("**Langkah 1 — Matriks Keputusan (Profil Rata-rata per Jenis Diet)**")
            st.dataframe(profil_diet[KRITERIA].round(4), use_container_width=True)

            st.markdown("**Langkah 2 — Normalisasi Min-Max**")
            st.caption("Cost: (max − x) / (max − min)   |   Benefit: (x − min) / (max − min)")
            st.dataframe(tbl_norm.round(6), use_container_width=True)

            st.markdown("**Langkah 3 — Vektor S dan Vektor V**")
            df_sv = pd.DataFrame({
                'Jenis Diet': list(profil_diet.index),
                'Vektor S'  : np.round(S_vals, 8),
                'Vektor V'  : np.round(V_vals, 8),
                'Peringkat' : [
                    sorted(range(len(V_vals)), key=lambda i: V_vals[i], reverse=True).index(i) + 1
                    for i in range(len(V_vals))
                ],
            })
            st.dataframe(df_sv, use_container_width=True, hide_index=True)

            st.markdown("""
**Rumus:**

$$S_i = \\prod_{j=1}^{n} x_{ij}^{w_j} \\qquad V_i = \\frac{S_i}{\\sum_{k=1}^{m} S_k}$$

- $S_i$ = vektor perkalian berbobot untuk diet ke-$i$  
- $V_i$ = nilai preferensi ternormalisasi (dasar peringkat)  
- $w_j$ = bobot kriteria ke-$j$ (ternormalisasi)  
- **Cost**: nilai asli lebih kecil = lebih baik  
- **Benefit**: nilai asli lebih besar = lebih baik
""")

        # Grafik perbandingan
        st.markdown('<div class="section-title">Grafik Perbandingan Nilai V</div>', unsafe_allow_html=True)
        fig_r, ax_r = plt.subplots(figsize=(8, 3))
        names_s = [r[0] for r in ranking]
        v_s     = [r[1] for r in ranking]
        col_s   = [DIET_COLOR[d] for d in names_s]
        hb = ax_r.barh(names_s[::-1], v_s[::-1], color=col_s[::-1], height=0.42, edgecolor='white')
        for bar, val in zip(hb, v_s[::-1]):
            ax_r.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height() / 2,
                      f"{val:.6f}", va='center', fontsize=10, fontweight='600', color='#333')
        ax_r.set_xlabel("Nilai V")
        ax_r.set_title(f"Perangkingan Jenis Diet — {nama}", fontweight='bold', fontsize=11)
        ax_r.set_xlim(0, max(v_s) * 1.3)
        ax_r.spines[['top', 'right']].set_visible(False)
        fig_r.tight_layout()
        st.pyplot(fig_r)
        plt.close(fig_r)

    else:
        st.markdown("""
        <div style="background:#f9fafb;border:1px solid #e0e0e0;border-radius:10px;
                    padding:40px;text-align:center;margin-top:20px;">
            <div style="font-size:1rem;color:#444;font-weight:600;">
                Lengkapi data pasien di atas, lalu klik <strong>Hitung Rekomendasi Diet</strong>
            </div>
            <div style="color:#888;margin-top:8px;font-size:0.875rem;">
                Sistem akan membandingkan kondisi pasien dengan profil tiga jenis diet
                (Balanced, Low_Carb, Low_Sodium) menggunakan metode Weighted Product.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VISUALISASI
# ══════════════════════════════════════════════════════════════════════════════
with tab_viz:
    # Matplotlib global style
    plt.rcParams.update({
        'axes.spines.top'   : False,
        'axes.spines.right' : False,
        'axes.grid'         : True,
        'grid.alpha'        : 0.3,
        'grid.linestyle'    : '--',
        'font.size'         : 9,
    })

    # ── Grafik 1: Bar Profil Kriteria ──────────────────────────────────────────
    st.markdown('<div class="section-title">Grafik 1 — Profil Rata-rata Kriteria per Jenis Diet</div>', unsafe_allow_html=True)
    st.caption("Perbandingan nilai rata-rata setiap kriteria antar tiga jenis diet.")
    fig1, axes1 = plt.subplots(1, 5, figsize=(15, 4))
    for i, k in enumerate(KRITERIA):
        vals   = [profil_diet.loc[d, k] for d in DIET_LIST]
        colors = [DIET_COLOR[d] for d in DIET_LIST]
        bars   = axes1[i].bar(DIET_LIST, vals, color=colors, edgecolor='white', width=0.5)
        axes1[i].set_title(LABEL_K[i], fontsize=8, fontweight='bold', pad=8)
        axes1[i].tick_params(axis='x', rotation=15, labelsize=7.5)
        axes1[i].set_ylabel("Rata-rata", fontsize=7.5)
        for bar, v in zip(bars, vals):
            axes1[i].text(bar.get_x() + bar.get_width() / 2,
                          bar.get_height() - (bar.get_height() * 0.07),
                          f"{v:.1f}", ha='center', va='top',
                          fontsize=7, color='white', fontweight='bold')
    patches1 = [mpatches.Patch(color=DIET_COLOR[d], label=d) for d in DIET_LIST]
    fig1.legend(handles=patches1, loc='upper right', fontsize=9, framealpha=0.9)
    fig1.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    st.divider()

    # ── Grafik 2 & 3 ──────────────────────────────────────────────────────────
    g2a, g2b = st.columns(2)

    with g2a:
        st.markdown('<div class="section-title">Grafik 2 — Heatmap Korelasi Antar Kriteria</div>', unsafe_allow_html=True)
        st.caption("Nilai mendekati 1 atau -1 menunjukkan korelasi kuat antar kriteria.")
        fig2, ax2 = plt.subplots(figsize=(6, 5))
        corr = df[KRITERIA].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        labels_short = ['BMI', 'Kalori', 'Olahraga', 'Kepatuhan', 'Imbalance']
        corr.index   = labels_short
        corr.columns = labels_short
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
                    cmap="RdYlGn", center=0, linewidths=0.5,
                    ax=ax2, annot_kws={"size": 9},
                    cbar_kws={"shrink": 0.8})
        ax2.set_title("Korelasi Antar Kriteria", fontweight='bold', pad=10)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    with g2b:
        st.markdown('<div class="section-title">Grafik 3 — Distribusi Rekomendasi Diet</div>', unsafe_allow_html=True)
        st.caption("Proporsi jumlah pasien per jenis diet dalam dataset.")
        fig3, ax3 = plt.subplots(figsize=(6, 5))
        counts     = df['Diet_Recommendation'].value_counts()
        col_pie    = [DIET_COLOR[d] for d in counts.index]
        wedges, texts, autotexts = ax3.pie(
            counts, labels=counts.index, autopct='%1.1f%%',
            colors=col_pie, startangle=140,
            wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
            textprops={"fontsize": 10},
        )
        for at in autotexts:
            at.set_fontweight('bold')
        ax3.set_title(f"Proporsi Jenis Diet  (n = {len(df)})", fontweight='bold', pad=10)
        fig3.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    st.divider()

    # ── Grafik 4: Boxplot ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Grafik 4 — Distribusi Nilai Kriteria per Jenis Diet</div>', unsafe_allow_html=True)
    st.caption("Boxplot menunjukkan sebaran, median, dan outlier nilai kriteria untuk setiap jenis diet.")
    fig4, axes4 = plt.subplots(1, 5, figsize=(16, 4.5))
    for i, k in enumerate(KRITERIA):
        data_bp = [df[df['Diet_Recommendation'] == d][k].dropna().values for d in DIET_LIST]
        bp = axes4[i].boxplot(
            data_bp, patch_artist=True,
            medianprops=dict(color='#212121', linewidth=2),
            whiskerprops=dict(color='#757575'),
            capprops=dict(color='#757575'),
            flierprops=dict(marker='o', markerfacecolor='#ef5350', markersize=3, linestyle='none'),
        )
        for patch, d in zip(bp['boxes'], DIET_LIST):
            patch.set_facecolor(DIET_COLOR[d] + '55')
            patch.set_edgecolor(DIET_COLOR[d])
            patch.set_linewidth(1.5)
        axes4[i].set_xticks([1, 2, 3])
        axes4[i].set_xticklabels(['Bal', 'L-Carb', 'L-Na'], fontsize=8)
        axes4[i].set_title(LABEL_K[i], fontsize=8, fontweight='bold', pad=8)
    patches4 = [mpatches.Patch(facecolor=DIET_COLOR[d]+'55', edgecolor=DIET_COLOR[d], linewidth=1.5, label=d) for d in DIET_LIST]
    fig4.legend(handles=patches4, loc='upper right', fontsize=9)
    fig4.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)

    st.divider()

    # ── Grafik 5 & 6 ──────────────────────────────────────────────────────────
    g5a, g5b = st.columns(2)

    with g5a:
        st.markdown('<div class="section-title">Grafik 5 — Sebaran BMI vs Kalori Harian</div>', unsafe_allow_html=True)
        st.caption("Setiap titik mewakili satu pasien, diwarnai berdasarkan jenis diet yang direkomendasikan.")
        fig5, ax5 = plt.subplots(figsize=(6, 4.5))
        for d in DIET_LIST:
            sub = df[df['Diet_Recommendation'] == d]
            ax5.scatter(sub['BMI'], sub['Daily_Caloric_Intake'],
                        label=d, color=DIET_COLOR[d],
                        alpha=0.7, s=35, edgecolors='white', linewidths=0.3)
        ax5.set_xlabel("BMI", fontsize=10)
        ax5.set_ylabel("Kalori Harian (kkal)", fontsize=10)
        ax5.set_title("Sebaran BMI vs Kalori Harian", fontweight='bold')
        ax5.legend(fontsize=9, framealpha=0.9)
        fig5.tight_layout()
        st.pyplot(fig5)
        plt.close(fig5)

    with g5b:
        st.markdown('<div class="section-title">Grafik 6 — Kepatuhan & Olahraga per Jenis Diet</div>', unsafe_allow_html=True)
        st.caption("Perbandingan rata-rata kepatuhan diet dan jam olahraga. Nilai olahraga dikali 10 agar skala sebanding.")
        fig6, ax6 = plt.subplots(figsize=(6, 4.5))
        x     = np.arange(len(DIET_LIST))
        w6    = 0.32
        avg_k = [profil_diet.loc[d, 'Adherence_to_Diet_Plan']  for d in DIET_LIST]
        avg_o = [profil_diet.loc[d, 'Weekly_Exercise_Hours']*10 for d in DIET_LIST]
        b1 = ax6.bar(x - w6/2, avg_k, w6, label='Kepatuhan (%)',      color='#43a047', edgecolor='white')
        b2 = ax6.bar(x + w6/2, avg_o, w6, label='Olahraga x10 (jam)', color='#1e88e5', edgecolor='white')
        ax6.set_xticks(x)
        ax6.set_xticklabels(DIET_LIST, fontsize=9)
        ax6.set_ylabel("Nilai")
        ax6.set_title("Rata-rata Kepatuhan & Olahraga per Diet", fontweight='bold')
        ax6.legend(fontsize=9, framealpha=0.9)
        for bar in list(b1) + list(b2):
            ax6.text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.3,
                     f"{bar.get_height():.1f}",
                     ha='center', fontsize=8, color='#333')
        fig6.tight_layout()
        st.pyplot(fig6)
        plt.close(fig6)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PROFIL KELOMPOK
# ══════════════════════════════════════════════════════════════════════════════
with tab_profil:

    st.markdown('<div class="section-title">Informasi Proyek</div>', unsafe_allow_html=True)
    st.markdown("""
| Info | Detail |
|---|---|
| **Mata Kuliah** | Sistem Pendukung Keputusan (SCPK) |
| **Judul** | SPK Pemilihan Jenis Diet untuk Penurunan Berat Badan |
| **Metode** | Weighted Product (WP) |
| **Dataset** | Diet Recommendations — 250 Pasien |
| **Alternatif** | Balanced, Low_Carb, Low_Sodium |
| **Tahun** | 2025 |
    """)

    st.divider()
    st.markdown('<div class="section-title">Anggota Kelompok</div>', unsafe_allow_html=True)

    members = [
        ("TAZKYA SYAKIEB DWININGTYAS", "123240029"),
        ("ANINDYA YOLA PUSPITA",        "123240199"),
    ]
    mc = st.columns(2)
    for col_m, (nama_m, nim_m) in zip(mc, members):
        with col_m:
            st.markdown(f"""
            <div style="background:#f9fafb;border:1px solid #e0e0e0;border-radius:10px;
                        padding:20px;text-align:center;">
                <div style="font-weight:700;font-size:1rem;color:#1b5e20">{nama_m}</div>
                <div style="color:#666;font-size:0.88rem;margin-top:6px">NIM: {nim_m}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="section-title">Dasar Teori Metode Weighted Product</div>', unsafe_allow_html=True)
    st.markdown("""
Weighted Product (WP) adalah metode pengambilan keputusan multi-kriteria (MADM) yang menggunakan
perkalian berbobot untuk mengevaluasi alternatif berdasarkan sejumlah kriteria.

Dalam proyek ini, **alternatif bukan pasien, melainkan tiga jenis diet**: Balanced, Low_Carb, dan Low_Sodium.
Setiap jenis diet direpresentasikan oleh profil rata-rata nilai kriteria dari pasien yang sudah terbukti
cocok dengan diet tersebut di dalam dataset.

**Rumus:**

$$S_i = \\prod_{j=1}^{n} x_{ij}^{\\,w_j} \\qquad V_i = \\frac{S_i}{\\sum_{k=1}^{m} S_k}$$

| Simbol | Keterangan |
|---|---|
| $S_i$ | Vektor S untuk jenis diet ke-$i$ |
| $V_i$ | Nilai preferensi ternormalisasi — semakin besar semakin direkomendasikan |
| $x_{ij}$ | Nilai normalisasi kriteria ke-$j$ dari profil diet ke-$i$ |
| $w_j$ | Bobot kriteria ke-$j$ (ternormalisasi, total = 1) |
| Cost | Nilai lebih kecil lebih baik: BMI, Kalori Harian, Skor Imbalance |
| Benefit | Nilai lebih besar lebih baik: Olahraga Mingguan, Kepatuhan Diet |
    """)

    st.divider()
    st.markdown('<div class="section-title">Preprocessing Dataset</div>', unsafe_allow_html=True)
    st.markdown("""
Dataset asli memiliki 20 kolom. Setelah preprocessing tersisa 14 kolom dengan 5 kriteria aktif untuk perhitungan WP.

**Kolom yang dihapus (6 kolom):**

| Kolom | Alasan |
|---|---|
| Cholesterol_mg/dL, Blood_Pressure_mmHg, Glucose_mg/dL | Tidak langsung berkaitan dengan mekanisme penurunan berat badan |
| Dietary_Restrictions, Allergies | Berupa batasan/constraint medis, bukan kriteria penilaian kuantitatif |
| Preferred_Cuisine | Preferensi budaya, tidak memengaruhi efektivitas diet |

Kolom `Weight_kg` dan `Height_cm` dipertahankan sebagai informasi pasien, namun tidak masuk
kriteria karena sudah terangkum dalam BMI. Kolom `Diet_Recommendation` tidak digunakan sebagai
kriteria, melainkan hanya sebagai referensi pembentuk profil tiap jenis diet.
    """)
