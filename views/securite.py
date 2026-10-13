"""
Onglet Sécurité routière : analyse nationale des accidents, blessés et morts.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard_data import load_kpi_national


# ---------- Palette ----------
BLEU_CHARRON = "#1F3A5F"
ROUGE_BRIQUE = "#B83232"
ORANGE_DOUX  = "#E8A33D"
VIOLET       = "#6B3FA0"
GRIS_REF     = "#888888"


def kpi_card(value, label, bg="#e6f4ec", icon="school"):
    return f"""
    <div style="background:{bg}; border-radius:12px; padding:14px 18px;
                margin-bottom:10px; position:relative; min-height:76px;
                box-shadow:0 1px 2px rgba(0,0,0,0.03);">
      <div style="font-family:Arial, sans-serif; font-size:21px; font-weight:700;
                  color:#000000; line-height:1.1;">{value}</div>
      <div style="font-family:Arial, sans-serif; font-size:12.5px; color:#3a4a44;
                  margin-top:4px; line-height:1.35; padding-right:42px;">{label}</div>
      <div style="position:absolute; right:14px; top:50%;
                  transform:translateY(-50%); color:#1F3A5F;">
        <span class="material-symbols-outlined" style="font-size:24px;">{icon}</span>
      </div>
    </div>
    """


def _base_layout(title, height=270):
    return dict(
        title=dict(text=title, font=dict(size=13, color="#1a3a2f")),
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=10)),
        showlegend=False,
    )


# ============================================================
# GRAPHIQUES
# ============================================================
def chart_evolution_accidents(df):
    fig = go.Figure(go.Scatter(
        x=df["annee"], y=df["nb_accidents"],
        mode="lines+markers",
        line=dict(color=BLEU_CHARRON, width=2.4),
        marker=dict(size=5),
        fill="tozeroy", fillcolor="rgba(31,58,95,0.10)",
        hovertemplate="<b>%{x}</b><br>Accidents : %{y:,}<extra></extra>",
    ))
    fig.update_layout(**_base_layout("Évolution du nombre d'accidents"))
    return fig


def chart_evolution_blesses(df):
    fig = go.Figure(go.Bar(
        x=df["annee"], y=df["nb_blesses"],
        marker_color=ORANGE_DOUX,
        hovertemplate="<b>%{x}</b><br>Blessés : %{y:,}<extra></extra>",
    ))
    fig.update_layout(**_base_layout("Évolution du nombre de blessés"))
    return fig


def chart_evolution_morts(df):
    fig = go.Figure(go.Scatter(
        x=df["annee"], y=df["nb_morts"],
        mode="lines+markers",
        line=dict(color=ROUGE_BRIQUE, width=2.4),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Morts : %{y:,}<extra></extra>",
    ))
    fig.update_layout(**_base_layout("Évolution du nombre de morts"))
    return fig


def chart_accidents_100k(df):
    fig = go.Figure(go.Scatter(
        x=df["annee"], y=df["accidents_pour_100k_hab"],
        mode="lines+markers",
        line=dict(color=VIOLET, width=2.4),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>%{y:.2f} / 100k hab.<extra></extra>",
    ))
    avg = df["accidents_pour_100k_hab"].mean()
    fig.add_hline(
        y=avg, line_dash="dash", line_color=GRIS_REF,
        annotation_text=f"Moy. {avg:.1f}",
        annotation_position="top right",
        annotation_font_size=10,
    )
    fig.update_layout(**_base_layout("Accidents pour 100 000 habitants"))
    return fig


def chart_donut_annee(df, annee):
    row = df[df["annee"] == annee].iloc[0]
    blesses = float(row["nb_blesses"])
    morts   = float(row["nb_morts"])
    total = blesses + morts

    fig = go.Figure(go.Pie(
        labels=["Blessés", "Morts"],
        values=[blesses, morts],
        hole=0.58,
        marker=dict(
            colors=[ORANGE_DOUX, ROUGE_BRIQUE],
            line=dict(color="white", width=2),
        ),
        textinfo="percent",
        textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=f"Répartition des victimes — {annee}",
                   font=dict(size=13, color="#1a3a2f")),
        height=270, margin=dict(l=10, r=10, t=40, b=10),
        showlegend=True,
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center",
                    font=dict(size=11)),
        annotations=[dict(
            text=f"<b>{int(total):,}</b><br>victimes".replace(",", " "),
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color=ROUGE_BRIQUE),
        )],
    )
    return fig


def chart_taux_mortalite(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["annee"], y=df["taux_mortalite_pct"],
        marker_color=ROUGE_BRIQUE, opacity=0.75,
        hovertemplate="<b>%{x}</b><br>Taux : %{y:.2f} %<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["annee"], y=df["taux_mortalite_pct"],
        mode="lines", line=dict(color=BLEU_CHARRON, width=2),
        hoverinfo="skip",
    ))
    fig.update_layout(**_base_layout("Taux de mortalité (% morts / accidents)"))
    return fig


# ============================================================
# TABLEAU
# ============================================================
def make_top_table(df, n=10):
    top = df.sort_values("nb_accidents", ascending=False).head(n).copy()
    top["rang"] = range(1, len(top) + 1)
    out = top[["rang", "annee", "nb_accidents", "nb_morts", "nb_blesses",
               "taux_mortalite_pct"]].copy()
    out.columns = ["#", "Année", "Accidents", "Morts", "Blessés", "Mortalité (%)"]
    return out


# ============================================================
# RENDER
# ============================================================
def render():
    df_full = load_kpi_national()
    df_full = df_full.dropna(subset=["nb_accidents"]).sort_values("annee").reset_index(drop=True)

    last = df_full.iloc[-1]

    # ---------- LAYOUT ----------
    c_left, c_right = st.columns([22, 78])

    # ============ COLONNE GAUCHE ============
    with c_left:
        st.markdown(
            kpi_card(f"{int(last['nb_accidents']):,}".replace(",", " "),
                     f"Accidents de la circulation ({int(last['annee'])})",
                     bg="#e6eff7", icon="car_crash"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{int(last['nb_morts']):,}".replace(",", " "),
                     f"Morts sur les routes ({int(last['annee'])})",
                     bg="#fbe6e6", icon="person_off"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{int(last['nb_blesses']):,}".replace(",", " "),
                     f"Blessés ({int(last['annee'])})",
                     bg="#fdefdd", icon="healing"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{last['accidents_pour_100k_hab']:.2f}",
                     "Accidents pour 100 000 habitants",
                     bg="#f0e8f5", icon="warning"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{last['morts_pour_100k_hab']:.2f}",
                     "Morts pour 100 000 habitants",
                     bg="#fbe6e6", icon="dangerous"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{last['taux_mortalite_pct']:.2f} %",
                     "Taux de mortalité (morts / accidents)",
                     bg="#e6f4ec", icon="percent"),
            unsafe_allow_html=True,
        )

        st.markdown(
            '<h3 style="font-size:14px; color:#1a3a2f; margin-top:10px;">'
            '<span class="material-symbols-outlined" '
            'style="font-size:18px; vertical-align:middle; margin-right:6px;">'
            'leaderboard</span>Top 10 années les plus meurtrières</h3>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            make_top_table(df_full, n=10),
            hide_index=True, use_container_width=True, height=340,
        )

    # ============ COLONNE DROITE ============
    with c_right:
        # --- Range slider période ---
        annee_min = int(df_full["annee"].min())
        annee_max = int(df_full["annee"].max())

        annee_debut, annee_fin = st.slider(
            "Période d'analyse",
            min_value=annee_min,
            max_value=annee_max,
            value=(annee_min, annee_max),
            step=1,
            key="sec_range",
        )

        df = df_full[
            (df_full["annee"] >= annee_debut) & (df_full["annee"] <= annee_fin)
        ].reset_index(drop=True)

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        # --- Ligne 1 ---
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            st.plotly_chart(chart_evolution_accidents(df),
                            use_container_width=True, key="sec_acc")
        with r1c2:
            st.plotly_chart(chart_evolution_blesses(df),
                            use_container_width=True, key="sec_bless")
        with r1c3:
            st.plotly_chart(chart_evolution_morts(df),
                            use_container_width=True, key="sec_morts")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        # --- Ligne 2 ---
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            st.plotly_chart(chart_accidents_100k(df),
                            use_container_width=True, key="sec_100k")

        with r2c2:
            years = sorted(df["annee"].unique(), reverse=True)
            annee_sel = st.selectbox(
                "Année",
                years, index=0, key="sec_annee_donut",
                label_visibility="collapsed",
            )
            st.plotly_chart(chart_donut_annee(df, annee_sel),
                            use_container_width=True, key="sec_donut")

        with r2c3:
            st.plotly_chart(chart_taux_mortalite(df),
                            use_container_width=True, key="sec_taux")