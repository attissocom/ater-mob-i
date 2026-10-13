"""
Onglet Accueil : hero banner + chiffres clés + graphiques synthétiques.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard_data import (
    load_kpi_national, load_kpi_regional, load_auto_ecoles,
)


# ---------- Palette ----------
BLEU_CHARRON = "#1F3A5F"
VERT_TOGO    = "#0b6b3a"
VERT_CLAIR   = "#d6f5e3"
ORANGE_DOUX  = "#E8A33D"
VIOLET       = "#6B3FA0"
ROUGE_BRIQUE = "#B83232"
JAUNE        = "#f4c20d"
BLEU_MOYEN   = "#2b5d8c"


# ============================================================
# HERO BANNER
# ============================================================
def _hero_banner():
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0b6b3a 0%, #1F3A5F 100%);
        border-radius: 18px;
        padding: 42px 30px 46px 30px;
        text-align: center;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    ">
      <div style="margin-bottom: 12px;">
        <span class="material-symbols-outlined"
              style="font-size: 78px; color: white; opacity: 0.95;">
          public
        </span>
      </div>
      <h1 style="font-family: Arial, sans-serif; font-size: 42px;
                 font-weight: 800; margin: 0 0 6px 0; letter-spacing: 1.5px;
                 color: white;">
        ATER-MOB I
      </h1>
      <h2 style="font-family: Arial, sans-serif; font-size: 20px;
                 font-weight: 400; margin: 0 0 22px 0;
                 color: rgba(255,255,255,0.95);">
        Dashboard Administration territoriale &amp; Mobilité - Togo
      </h2>
      <p style="font-family: Arial, sans-serif; font-size: 15px;
                line-height: 1.6; max-width: 900px; margin: 0 auto;
                color: rgba(255,255,255,0.92);">
        Dashboard de visualisation et d'analyse des données sur
        l'<b>immatriculation des véhicules</b>, les <b>permis de conduire</b>,
        les <b>accidents de la route</b>, l'<b>état du réseau routier</b> et
        le <b>maillage des auto-écoles</b>, pour une mobilité plus sûre et
        mieux planifiée au Togo.
      </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# KPI CARD — variante compacte pour l'accueil
# ============================================================
def _kpi_hero(value, label, icon="insights", accent=BLEU_CHARRON):
    return f"""
    <div style="
        background: white;
        border-radius: 14px;
        padding: 20px 18px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border-top: 4px solid {accent};
        min-height: 130px;
    ">
      <div style="color: {accent}; margin-bottom: 8px;">
        <span class="material-symbols-outlined"
              style="font-size: 30px;">{icon}</span>
      </div>
      <div style="font-family: Arial, sans-serif; font-size: 26px;
                  font-weight: 800; color: #000; line-height: 1.1;">
        {value}
      </div>
      <div style="font-family: Arial, sans-serif; font-size: 12.5px;
                  color: #3a4a44; margin-top: 8px; line-height: 1.4;">
        {label}
      </div>
    </div>
    """


# ============================================================
# GRAPHIQUES SYNTHÉTIQUES
# ============================================================
def _chart_mobilite_express(df):
    """Évolution immat total + motos — focus sur la croissance."""
    df = df.dropna(subset=["immat_total"]).sort_values("annee")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["annee"], y=df["immat_total"],
        mode="lines", name="Total",
        line=dict(color=BLEU_CHARRON, width=2.6),
        fill="tozeroy", fillcolor="rgba(31,58,95,0.10)",
        hovertemplate="<b>%{x}</b><br>Total : %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["annee"], y=df["immat_motos"],
        mode="lines", name="2 roues",
        line=dict(color=ORANGE_DOUX, width=2.6),
        hovertemplate="<b>%{x}</b><br>2 roues : %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Immatriculations annuelles (1990 – 2022)",
                   font=dict(size=14, color="#1a3a2f")),
        height=320, margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=10),
                   tickformat=","),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center",
                    font=dict(size=11)),
    )
    return fig


def _chart_securite_express(df):
    """Accidents vs morts sur double axe Y."""
    df = df.dropna(subset=["nb_accidents"]).sort_values("annee")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["annee"], y=df["nb_accidents"], name="Accidents",
        marker_color=BLEU_MOYEN, opacity=0.75,
        hovertemplate="<b>%{x}</b><br>Accidents : %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["annee"], y=df["nb_morts"], name="Morts",
        mode="lines+markers",
        line=dict(color=ROUGE_BRIQUE, width=2.6),
        marker=dict(size=4),
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Morts : %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Sécurité routière — accidents vs morts",
                   font=dict(size=14, color="#1a3a2f")),
        height=320, margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=10),
                   tickformat=",", title=None),
        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                    tickfont=dict(size=10), title=None),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center",
                    font=dict(size=11)),
    )
    return fig


def _chart_permis_express(df):
    """Répartition des permis délivrés par catégorie — année la plus récente."""
    df_last = df.dropna(subset=["permis_total"]).sort_values("annee").iloc[-1]
    annee = int(df_last["annee"])

    cats = {
        "permis_A": ("A — Moto", ORANGE_DOUX),
        "permis_B": ("B — Voiture", BLEU_CHARRON),
        "permis_C": ("C — Poids lourd", VIOLET),
        "permis_D": ("D — Transport commun", ROUGE_BRIQUE),
        "permis_E": ("E — Semi-remorque", VERT_TOGO),
        "permis_F": ("F — Voiture spéciale", JAUNE),
    }
    labels, values, colors = [], [], []
    for col, (label, color) in cats.items():
        if col in df.columns:
            v = df_last[col]
            if v > 0:
                labels.append(label)
                values.append(float(v))
                colors.append(color)

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="percent",
        textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
    ))
    total = sum(values)
    fig.update_layout(
        title=dict(text=f"Permis délivrés par catégorie — {annee}",
                   font=dict(size=14, color="#1a3a2f")),
        height=320, margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10)),
        annotations=[dict(
            text=f"<b>{int(total):,}</b><br>permis".replace(",", " "),
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color=VERT_TOGO),
        )],
    )
    return fig


# ============================================================
# SECTION TITRE
# ============================================================
def _section_title(text, icon="insights"):
    st.markdown(f"""
    <h2 style="font-family: Arial, sans-serif; font-size: 24px;
               font-weight: 700; color: #0b3d2a; margin: 20px 0 18px 0;
               text-align: center;">
      <span class="material-symbols-outlined"
            style="font-size: 26px; vertical-align: middle;
                   margin-right: 10px; color: {VERT_TOGO};">
        {icon}
      </span>{text}
    </h2>
    """, unsafe_allow_html=True)


# ============================================================
# RENDER
# ============================================================
def render():
    # ---------- 1. HERO ----------
    _hero_banner()

    # ---------- 2. CHIFFRES CLÉS ----------
    _section_title("Les chiffres clés : 2022", icon="bar_chart")

    df_nat = load_kpi_national()
    df_reg = load_kpi_regional()
    auto = load_auto_ecoles()

    last = df_nat.dropna(subset=["immat_total"]).iloc[-1]
    annee = int(last["annee"])

    # Évolution immat 2018 → 2022
    d2018 = df_nat[df_nat["annee"] == 2018]
    immat_2018 = int(d2018["immat_total"].iloc[0]) if len(d2018) else 0
    evol_immat = ((last["immat_total"] - immat_2018) / immat_2018 * 100
                  if immat_2018 else 0)

    # Part motos
    part_motos = last["part_motos_pct"]

    # Auto-écoles
    nb_auto = len(auto)
    top_reg_auto = (
        df_reg.sort_values("auto_ecoles_pour_100k_hab", ascending=False)
        .iloc[0]["region"].title()
    )

    # Sécurité
    nb_acc = int(last["nb_accidents"])
    nb_morts = int(last["nb_morts"])
    taux_mort = last["taux_mortalite_pct"]

    # Population
    pop = int(last["population"])

    # Grille 6 KPI
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        st.markdown(
            _kpi_hero(f"{int(last['immat_total']):,}".replace(",", " "),
                      f"Véhicules immatriculés<br><b style='color:{VERT_TOGO}'>"
                      f"+{evol_immat:.0f}%</b> vs 2018",
                      icon="directions_car", accent=BLEU_CHARRON),
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            _kpi_hero(f"{part_motos:.0f} %",
                      "Part des 2 roues dans<br>les immatriculations",
                      icon="two_wheeler", accent=ORANGE_DOUX),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            _kpi_hero(f"{nb_acc:,}".replace(",", " "),
                      "Accidents de la circulation",
                      icon="car_crash", accent=ROUGE_BRIQUE),
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            _kpi_hero(f"{nb_morts:,}".replace(",", " "),
                      f"Morts sur les routes<br>({taux_mort:.1f}% des accidents)",
                      icon="person_off", accent=ROUGE_BRIQUE),
            unsafe_allow_html=True,
        )
    with k5:
        st.markdown(
            _kpi_hero(f"{nb_auto:,}".replace(",", " "),
                      f"Auto-écoles recensées<br>Top région : {top_reg_auto}",
                      icon="school", accent=VIOLET),
            unsafe_allow_html=True,
        )
    with k6:
        st.markdown(
            _kpi_hero(f"{pop/1e6:.1f} M",
                      "Population du Togo<br>(projection 2022)",
                      icon="groups", accent=VERT_TOGO),
            unsafe_allow_html=True,
        )

    # ---------- 3. GRAPHIQUES SYNTHÉTIQUES ----------
    _section_title("Les tendances structurantes", icon="trending_up")

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(_chart_mobilite_express(df_nat),
                        width="stretch", key="acc_g1")
    with g2:
        st.plotly_chart(_chart_securite_express(df_nat),
                        width="stretch", key="acc_g2")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    g3_l, g3_m, g3_r = st.columns([1, 2, 1])
    with g3_m:
        st.plotly_chart(_chart_permis_express(df_nat),
                        width="stretch", key="acc_g3")

    # ---------- 4. PIED DE PAGE CONTEXTUEL ----------
    st.markdown(f"""
    <div style="
        background: #f6fbf8;
        border-left: 5px solid {VERT_TOGO};
        border-radius: 12px;
        padding: 18px 22px;
        margin-top: 32px;
        font-family: Arial, sans-serif;
        font-size: 13.5px;
        color: #3a4a44;
        line-height: 1.65;
    ">
      <b style="color:{VERT_TOGO}; font-size:14.5px;">
        À propos de ce tableau de bord
      </b><br>
      Ce dashboard rassemble et met en regard les données ouvertes sur
      <b>l'immatriculation des véhicules</b>, les <b>permis de conduire</b>,
      les <b>accidents de la circulation</b>, <b>l'état du réseau routier</b>,
      le <b>maillage des auto-écoles</b> et la <b>démographie</b>
      (RGPH5). Il permet de suivre l'évolution de la mobilité au Togo de
      <b>1990 à 2022</b> et d'identifier les zones à prioriser pour
      l'amélioration de la sécurité routière et de la desserte en
      infrastructures. Il est élaboré dans le cadre du Data Challenge domaine Administration territoriale et Mobilité organisé par TOGO AI LAB 
    </div>
    """, unsafe_allow_html=True)