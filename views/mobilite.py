"""
Onglet Mobilité : immatriculations, permis, structure du parc.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard_data import load_kpi_national


# ---------- Palette ----------
BLEU_CHARRON = "#1F3A5F"
VERT_TOGO    = "#0b6b3a"
ORANGE_DOUX  = "#E8A33D"
VIOLET       = "#6B3FA0"
JAUNE_OCRE   = "#C9A227"
GRIS_BLEU    = "#5C7A99"
BLEU_CLAIR   = "#5B8DC7"
VERT_OLIVE   = "#7A8B4A"
ROUGE_BRIQUE = "#B83232"

# Mapping : colonne kpi_national -> (label court, couleur)
TYPES_VEHICULES = {
    "immat_motos":           ("2 R et assimilées",  ORANGE_DOUX),
    "immat_voitures":        ("Voitures",           BLEU_CLAIR),
    "immat_camionnettes":    ("Camionnettes",       VERT_OLIVE),
    "immat_camions":         ("Camions",            VIOLET),
    "immat_semi_remorques":  ("Semi-remorques",     ROUGE_BRIQUE),
    "immat_tracteurs":       ("Tracteurs",          JAUNE_OCRE),
    "immat_autocars":        ("Autocars/Autobus",   GRIS_BLEU),
}

CATEGORIES_PERMIS = {
    "permis_A": ("A — Moto",                 ORANGE_DOUX),
    "permis_B": ("B — Voiture légère",       BLEU_CLAIR),
    "permis_C": ("C — Poids lourd",          VIOLET),
    "permis_D": ("D — Transport en commun",  ROUGE_BRIQUE),
    "permis_E": ("E — Semi-remorque",        VERT_TOGO),
    "permis_F": ("F — Voiture spéciale",     JAUNE_OCRE),
}


# ============================================================
# KPI CARD
# ============================================================
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
        height=height, margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=10)),
    )


# ============================================================
# GRAPHIQUES
# ============================================================
def chart_immat_vs_permis(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["annee"], y=df["immat_total"],
        mode="lines+markers", name="Immatriculations",
        line=dict(color=BLEU_CHARRON, width=2.4),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Immat : %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["annee"], y=df["permis_total"],
        mode="lines+markers", name="Permis",
        line=dict(color=VERT_TOGO, width=2.4, dash="dot"),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Permis : %{y:,}<extra></extra>",
    ))
    layout = _base_layout("Évolution immatriculations vs permis")
    layout["showlegend"] = True
    layout["legend"] = dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                            font=dict(size=11))
    fig.update_layout(**layout)
    return fig


def chart_immat_par_type(df, mode="volume"):
    """
    mode = "volume"  → valeurs absolues en courbes
    mode = "part"    → % du total annuel, en aires empilées 100 %
    """
    df = df.copy()

    if mode == "part":
        # Calcul des parts en %
        cols = [c for c in TYPES_VEHICULES if c in df.columns]
        total = df[cols].sum(axis=1).replace(0, pd.NA)
        for c in cols:
            df[c] = (df[c] / total * 100).fillna(0)

        fig = go.Figure()
        for col, (label, color) in TYPES_VEHICULES.items():
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df["annee"], y=df[col],
                    mode="lines", name=label,
                    stackgroup="one",
                    line=dict(width=0.5, color=color),
                    fillcolor=color,
                    hovertemplate=f"<b>%{{x}}</b><br>{label} : %{{y:.1f}} %<extra></extra>",
                ))
        title = "Part des immatriculations par type (%)"
        ymax = 100
    else:
        fig = go.Figure()
        for col, (label, color) in TYPES_VEHICULES.items():
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df["annee"], y=df[col],
                    mode="lines", name=label,
                    line=dict(color=color, width=2),
                    hovertemplate=f"<b>%{{x}}</b><br>{label} : %{{y:,}}<extra></extra>",
                ))
        title = "Évolution des immatriculations par type"
        ymax = None

    layout = _base_layout(title)
    layout["showlegend"] = True
    layout["legend"] = dict(
        orientation="h", y=-0.25, x=0.5, xanchor="center",
        font=dict(size=9),
    )
    fig.update_layout(**layout)
    if ymax:
        fig.update_yaxes(range=[0, ymax], ticksuffix=" %")
    return fig


def chart_permis_par_categorie(df):
    fig = go.Figure()
    for col, (label, color) in CATEGORIES_PERMIS.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["annee"], y=df[col],
                mode="lines", name=label,
                line=dict(color=color, width=2),
                hovertemplate=f"<b>%{{x}}</b><br>{label} : %{{y:,}}<extra></extra>",
            ))
    layout = _base_layout("Évolution des permis par catégorie")
    layout["showlegend"] = True
    layout["legend"] = dict(orientation="h", y=-0.25, x=0.5, xanchor="center",
                            font=dict(size=9))
    fig.update_layout(**layout)
    return fig


def chart_donut_type(df, annee):
    row = df[df["annee"] == annee].iloc[0]
    labels, values, colors = [], [], []
    for col, (label, color) in TYPES_VEHICULES.items():
        if col in df.columns and row[col] > 0:
            labels.append(label)
            values.append(float(row[col]))
            colors.append(color)

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="percent",
        textfont=dict(size=11, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
    ))
    total = sum(values)
    fig.update_layout(
        title=dict(text=f"Structure du parc — {annee}",
                   font=dict(size=13, color="#1a3a2f")),
        height=270, margin=dict(l=10, r=10, t=40, b=10),
        showlegend=True,
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=9)),
        annotations=[dict(
            text=f"<b>{int(total):,}</b><br>véhicules".replace(",", " "),
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=BLEU_CHARRON),
        )],
    )
    return fig


def chart_donut_permis(df, annee):
    row = df[df["annee"] == annee].iloc[0]
    labels, values, colors = [], [], []
    for col, (label, color) in CATEGORIES_PERMIS.items():
        if col in df.columns and row[col] > 0:
            labels.append(label)
            values.append(float(row[col]))
            colors.append(color)

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="percent",
        textfont=dict(size=11, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
    ))
    total = sum(values)
    fig.update_layout(
        title=dict(text=f"Structure des permis — {annee}",
                   font=dict(size=13, color="#1a3a2f")),
        height=270, margin=dict(l=10, r=10, t=40, b=10),
        showlegend=True,
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=9)),
        annotations=[dict(
            text=f"<b>{int(total):,}</b><br>permis".replace(",", " "),
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=VERT_TOGO),
        )],
    )
    return fig


def chart_deux_vs_quatre_roues(df):
    df = df.copy()
    df["deux_roues"] = df["immat_motos"].fillna(0)
    df["quatre_roues"] = (
        df.get("immat_voitures", 0).fillna(0)
        + df.get("immat_camionnettes", 0).fillna(0)
        + df.get("immat_camions", 0).fillna(0)
        + df.get("immat_semi_remorques", 0).fillna(0)
        + df.get("immat_tracteurs", 0).fillna(0)
        + df.get("immat_autocars", 0).fillna(0)
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["annee"], y=df["deux_roues"], name="2 roues",
        marker_color=ORANGE_DOUX,
        hovertemplate="<b>%{x}</b><br>2 roues : %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df["annee"], y=df["quatre_roues"], name="4 roues et +",
        marker_color=BLEU_CHARRON,
        hovertemplate="<b>%{x}</b><br>4 roues : %{y:,}<extra></extra>",
    ))
    layout = _base_layout("Deux-roues vs quatre-roues et plus")
    layout["barmode"] = "stack"
    layout["showlegend"] = True
    layout["legend"] = dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                            font=dict(size=11))
    fig.update_layout(**layout)
    return fig


# ============================================================
# TABLEAU
# ============================================================
def make_structure_table(df):
    rows = []
    total = df["immat_total"].sum()
    for col, (label, _) in TYPES_VEHICULES.items():
        if col in df.columns:
            s = df[col].sum()
            rows.append({
                "Type": label,
                "Total (période)": int(s),
                "Part (%)": round(s / total * 100, 2) if total else 0,
            })
    out = pd.DataFrame(rows).sort_values("Total (période)", ascending=False)
    out["Total (période)"] = out["Total (période)"].apply(
        lambda x: f"{x:,}".replace(",", " ")
    )
    return out


# ============================================================
# RENDER
# ============================================================
def render():
    df_full = load_kpi_national()
    df_full = df_full.dropna(subset=["immat_total"]).sort_values("annee").reset_index(drop=True)

    c_left, c_right = st.columns([22, 78])

    # ============ COLONNE GAUCHE ============
    with c_left:
        st.markdown(
            '<h3 style="font-size:14px; color:#1a3a2f; margin-bottom:12px;">'
            '<span class="material-symbols-outlined" '
            'style="font-size:18px; vertical-align:middle; margin-right:6px;">'
            'tune</span>Sélection de la période</h3>',
            unsafe_allow_html=True,
        )
        annee_min = int(df_full["annee"].min())
        annee_max = int(df_full["annee"].max())
        annee_debut, annee_fin = st.slider(
            "Période",
            min_value=annee_min, max_value=annee_max,
            value=(annee_min, annee_max), step=1,
            key="mob_range", label_visibility="collapsed",
        )

    df = df_full[
        (df_full["annee"] >= annee_debut) & (df_full["annee"] <= annee_fin)
    ].reset_index(drop=True)

    # --- KPI ---
    total_immat = int(df["immat_total"].sum())
    total_permis = int(df["permis_total"].sum()) if "permis_total" in df.columns else 0

    # Type dominant
    type_totaux = {col: df[col].sum() for col in TYPES_VEHICULES if col in df.columns}
    top_type_col = max(type_totaux, key=type_totaux.get) if type_totaux else None
    top_type_label = TYPES_VEHICULES[top_type_col][0] if top_type_col else "—"

    # Catégorie permis dominante
    perms_totaux = {col: df[col].sum() for col in CATEGORIES_PERMIS if col in df.columns}
    top_perm_col = max(perms_totaux, key=perms_totaux.get) if perms_totaux else None
    top_perm_label = CATEGORIES_PERMIS[top_perm_col][0] if top_perm_col else "—"

    ratio = total_permis / total_immat if total_immat else 0

    with c_left:
        st.markdown(
            kpi_card(f"{total_immat:,}".replace(",", " "),
                     f"Véhicules immatriculés<br>"
                     f"<span style='font-size:11px;color:#6b7f76;'>{annee_debut} – {annee_fin}</span>",
                     bg="#e6eff7", icon="directions_car"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{total_permis:,}".replace(",", " "),
                     f"Permis délivrés<br>"
                     f"<span style='font-size:11px;color:#6b7f76;'>{annee_debut} – {annee_fin}</span>",
                     bg="#e6f4ec", icon="badge"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{top_type_label}",
                     "Type de véhicule le plus immatriculé",
                     bg="#fdefdd", icon="two_wheeler"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{top_perm_label}",
                     "Catégorie de permis la plus délivrée",
                     bg="#f0e8f5", icon="id_card"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{ratio:.2f}",
                     "Permis délivrés / véhicules immatriculés",
                     bg="#fbe6e6", icon="percent"),
            unsafe_allow_html=True,
        )

        st.markdown(
            '<h3 style="font-size:14px; color:#1a3a2f; margin-top:10px;">'
            '<span class="material-symbols-outlined" '
            'style="font-size:18px; vertical-align:middle; margin-right:6px;">'
            'table_chart</span>Récapitulatif par type</h3>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            make_structure_table(df),
            hide_index=True, use_container_width=True, height=340,
        )

    # ============ COLONNE DROITE ============
    with c_right:
        # Ligne 1
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            st.plotly_chart(chart_immat_vs_permis(df),
                            use_container_width=True, key="mob_vs")
        with r1c2:
            mode_immat = st.radio(
                "Affichage",
                ["Volume", "Part (%)"],
                horizontal=True,
                key="mob_type_mode",
                label_visibility="collapsed",
            )
            st.plotly_chart(
                chart_immat_par_type(df, mode="part" if mode_immat == "Part (%)" else "volume"),
                use_container_width=True, key="mob_type",
            )
        with r1c3:
            st.plotly_chart(chart_permis_par_categorie(df),
                            use_container_width=True, key="mob_perm")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        # Ligne 2
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            annee_a = st.selectbox(
                "Année (parc)", sorted(df["annee"].unique(), reverse=True),
                index=0, key="mob_an_parc", label_visibility="collapsed",
            )
            st.plotly_chart(chart_donut_type(df, annee_a),
                            use_container_width=True, key="mob_donut_parc")
        with r2c2:
            annee_b = st.selectbox(
                "Année (permis)", sorted(df["annee"].unique(), reverse=True),
                index=0, key="mob_an_perm", label_visibility="collapsed",
            )
            st.plotly_chart(chart_donut_permis(df, annee_b),
                            use_container_width=True, key="mob_donut_perm")
        with r2c3:
            st.plotly_chart(chart_deux_vs_quatre_roues(df),
                            use_container_width=True, key="mob_2vs4")