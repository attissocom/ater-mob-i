"""
Onglet Infrastructures & Réseau routier :
  - Sous-onglet 1 : État du réseau routier (reseau_routier_clean)
  - Sous-onglet 2 : Routes classées (routes_classees_enriched) + carte
"""
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

from src.dashboard_data import (
    load_reseau_routier, load_routes_classees, load_kpi_national,
)


# ---------- Palette ----------
BLEU_CHARRON = "#1F3A5F"
VERT_TOGO    = "#0b6b3a"
JAUNE        = "#f4c20d"
ROUGE_BRIQUE = "#B83232"
BLEU_MOYEN   = "#2b5d8c"
TERRE        = "#8B6F47"
OCRE         = "#C9A227"
GRIS_REF     = "#888888"

ETAT_COLORS = {
    "BON":     VERT_TOGO,
    "MOYEN":   JAUNE,
    "MAUVAIS": ROUGE_BRIQUE,
    "TRAVAUX": BLEU_MOYEN,
}

REVET_COLORS = {
    "revetue": BLEU_CHARRON,
    "terre":   TERRE,
}


# ============================================================
# KPI CARD (pattern validé)
# ============================================================
def kpi_card(value, label, bg="#e6f4ec", icon="school"):
    return f"""
    <div style="background:{bg}; border-radius:12px; padding:14px 18px;
                margin-bottom:10px; position:relative; min-height:76px;
                box-shadow:0 1px 2px rgba(0,0,0,0.03);">
      <div style="font-family:Arial, sans-serif; font-size:20px; font-weight:700;
                  color:#000000; line-height:1.1;">{value}</div>
      <div style="font-family:Arial, sans-serif; font-size:12.5px; color:#3a4a44;
                  margin-top:4px; line-height:1.35; padding-right:42px;">{label}</div>
      <div style="position:absolute; right:14px; top:50%;
                  transform:translateY(-50%); color:#1F3A5F;">
        <span class="material-symbols-outlined" style="font-size:24px;">{icon}</span>
      </div>
    </div>
    """


def _base_layout(title, height=280):
    return dict(
        title=dict(text=title, font=dict(size=13, color="#1a3a2f")),
        height=height, margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=10)),
    )


# ################################################################
# SOUS-ONGLET 1 — ÉTAT DU RÉSEAU ROUTIER
# ################################################################
def _filters_reseau(df):
    """Filtres compactes : Catégorie / Revêtement / État."""
    c1, c2, c3 = st.columns(3)
    cats = ["Tout"] + sorted(df["categorie"].dropna().unique().tolist())
    cat = c1.selectbox("Catégorie", cats, key="ifr_cat")

    revs = ["Tout"] + sorted(df["revetement"].dropna().unique().tolist())
    rev = c2.selectbox("Revêtement", revs, key="ifr_rev")

    etats = sorted(df["etat"].dropna().unique().tolist())
    etat_sel = c3.multiselect("État", etats, default=etats, key="ifr_etat")

    d = df.copy()
    if cat != "Tout":
        d = d[d["categorie"] == cat]
    if rev != "Tout":
        d = d[d["revetement"] == rev]
    if etat_sel:
        d = d[d["etat"].isin(etat_sel)]
    return d, cat, rev


def _chart_donut_etat(df):
    counts = df.groupby("etat")["valeur"].sum().reset_index()
    colors = [ETAT_COLORS.get(e, "#888") for e in counts["etat"]]
    fig = go.Figure(go.Pie(
        labels=counts["etat"], values=counts["valeur"], hole=0.55,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="percent", textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value:.2f} km<extra></extra>",
    ))
    total = counts["valeur"].sum()
    fig.update_layout(
        title=dict(text="Répartition par état", font=dict(size=13, color="#1a3a2f")),
        height=280, margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center",
                    font=dict(size=11)),
        annotations=[dict(text=f"<b>{total:,.0f}</b><br>km".replace(",", " "),
                          x=0.5, y=0.5, showarrow=False,
                          font=dict(size=13, color=BLEU_CHARRON))],
    )
    return fig


def _chart_pct_bon_par_region(df_route_classee, df_reseau):
    """
    Barres 100% empilées : pour chaque région, % de chaque état.
    ⚠️ La région n'est pas dans reseau_routier → on utilise la jointure via code
    (retourne un message si jointure indisponible).
    Pour le moment, on agrège au niveau catégorie/revêtement.
    """
    # Fallback : barres empilées 100% par revêtement × état
    pivot = df_reseau.pivot_table(
        index=["categorie", "revetement"], columns="etat",
        values="valeur", aggfunc="sum", fill_value=0,
    )
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
    pivot_pct = pivot_pct.reset_index()
    pivot_pct["label"] = pivot_pct["categorie"] + " " + pivot_pct["revetement"]

    fig = go.Figure()
    for etat in ["BON", "MOYEN", "MAUVAIS", "TRAVAUX"]:
        if etat in pivot_pct.columns:
            fig.add_trace(go.Bar(
                y=pivot_pct["label"], x=pivot_pct[etat],
                name=etat, orientation="h",
                marker_color=ETAT_COLORS[etat],
                hovertemplate=f"<b>%{{y}}</b><br>{etat} : %{{x:.1f}} %<extra></extra>",
            ))
    layout = _base_layout("État du réseau par type (barres 100 %)")
    layout["barmode"] = "stack"
    layout["showlegend"] = True
    layout["legend"] = dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                            font=dict(size=10))
    fig.update_layout(**layout)
    fig.update_xaxes(range=[0, 100], ticksuffix=" %")
    return fig


def _chart_longueur_revetement(df_reseau):
    agg = df_reseau.groupby(["categorie", "revetement"])["valeur"].sum().reset_index()
    agg["label"] = agg["categorie"] + " — " + agg["revetement"]
    colors = [REVET_COLORS.get(r, "#888") for r in agg["revetement"]]
    fig = go.Figure(go.Bar(
        x=agg["label"], y=agg["valeur"],
        marker_color=colors,
        text=agg["valeur"].round(1),
        textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>%{y:.2f} km<extra></extra>",
    ))
    layout = _base_layout("Longueur par type de revêtement")
    layout["showlegend"] = False
    fig.update_layout(**layout)
    fig.update_xaxes(tickangle=-15)
    return fig


def _chart_classement_regions(df_reseau):
    """
    ⚠️ Pas de région dans reseau_routier → on affiche par tronçon
    (top 10 des tronçons les plus en mauvais état).
    """
    mauvais = df_reseau[df_reseau["etat"] == "MAUVAIS"]
    top = (
        mauvais.groupby("troncon")["valeur"].sum()
        .sort_values(ascending=False).head(10).reset_index()
    )
    top = top.sort_values("valeur", ascending=True)
    fig = go.Figure(go.Bar(
        x=top["valeur"], y=top["troncon"], orientation="h",
        marker_color=ROUGE_BRIQUE,
        text=top["valeur"].round(1),
        textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>%{x:.2f} km en mauvais état<extra></extra>",
    ))
    layout = _base_layout("Top 10 tronçons les plus dégradés (km MAUVAIS)")
    layout["showlegend"] = False
    fig.update_layout(**layout)
    fig.update_yaxes(tickfont=dict(size=9))
    return fig


def _chart_fret_routier_vs_rail(df_nat):
    """Bonus : comparaison fret routier vs fret rail (normalisé base 100)."""
    df = df_nat.dropna(subset=["fret_routier", "fret_rail"]).copy()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**_base_layout("Fret routier vs rail — données indisponibles"))
        return fig

    base = df.iloc[0]
    df["fret_routier_idx"] = df["fret_routier"] / base["fret_routier"] * 100
    df["fret_rail_idx"]    = df["fret_rail"]    / base["fret_rail"]    * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["annee"], y=df["fret_routier_idx"],
        mode="lines+markers", name="Fret routier",
        line=dict(color=BLEU_CHARRON, width=2.4),
        hovertemplate="<b>%{x}</b><br>Indice : %{y:.1f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["annee"], y=df["fret_rail_idx"],
        mode="lines+markers", name="Fret rail",
        line=dict(color=ROUGE_BRIQUE, width=2.4, dash="dot"),
        hovertemplate="<b>%{x}</b><br>Indice : %{y:.1f}<extra></extra>",
    ))
    layout = _base_layout("Fret routier vs fret rail (base 100)")
    layout["showlegend"] = True
    layout["legend"] = dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                            font=dict(size=11))
    fig.update_layout(**layout)
    fig.update_yaxes(title_text="Indice base 100")
    return fig


def _table_troncons_degrades(df_reseau, n=10):
    mauvais = df_reseau[df_reseau["etat"] == "MAUVAIS"]
    top = (
        mauvais.groupby(["troncon", "categorie", "revetement"])["valeur"]
        .sum().reset_index()
        .sort_values("valeur", ascending=False).head(n)
    )
    top["rang"] = range(1, len(top) + 1)
    top = top[["rang", "troncon", "categorie", "revetement", "valeur"]]
    top.columns = ["#", "Tronçon", "Type", "Revêtement", "Km mauvais"]
    top["Km mauvais"] = top["Km mauvais"].round(2)
    return top

def render_etat_reseau():
    df_full = load_reseau_routier()
    df_nat = load_kpi_national()

    c_left, c_right = st.columns([22, 78])

    # ---------- Colonne gauche : filtres + KPI + tableau ----------
    with c_left:
        st.markdown(
            '<h3 style="font-size:14px; color:#1a3a2f; margin-bottom:8px;">'
            '<span class="material-symbols-outlined" '
            'style="font-size:18px; vertical-align:middle; margin-right:6px;">'
            'filter_alt</span>Filtres</h3>',
            unsafe_allow_html=True,
        )
        cats = ["Tout"] + sorted(df_full["categorie"].dropna().unique().tolist())
        cat = st.selectbox("Catégorie", cats, key="ifr_cat")

        revs = ["Tout"] + sorted(df_full["revetement"].dropna().unique().tolist())
        rev = st.selectbox("Revêtement", revs, key="ifr_rev")

        etats = sorted(df_full["etat"].dropna().unique().tolist())
        etat_sel = st.multiselect("État", etats, default=etats, key="ifr_etat")

        df = df_full.copy()
        if cat != "Tout":
            df = df[df["categorie"] == cat]
        if rev != "Tout":
            df = df[df["revetement"] == rev]
        if etat_sel:
            df = df[df["etat"].isin(etat_sel)]

        total_km = df["valeur"].sum()
        bon_km = df[df["etat"] == "BON"]["valeur"].sum()
        mauvais_km = df[df["etat"] == "MAUVAIS"]["valeur"].sum()
        travaux_km = df[df["etat"] == "TRAVAUX"]["valeur"].sum()
        pct_bon = (bon_km / total_km * 100) if total_km else 0
        pct_mauvais = (mauvais_km / total_km * 100) if total_km else 0

        st.markdown(
            kpi_card(f"{total_km:,.0f} km".replace(",", " "),
                     "Longueur totale du périmètre filtré",
                     bg="#e6eff7", icon="add_road"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{pct_bon:.1f} %", "Réseau en bon état",
                     bg="#e6f4ec", icon="check_circle"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{pct_mauvais:.1f} %", "Réseau en mauvais état",
                     bg="#fbe6e6", icon="warning"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{travaux_km:,.0f} km".replace(",", " "),
                     "Longueur en travaux",
                     bg="#fdefdd", icon="construction"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card("548 km", "Réseau ferré national (constant)",
                     bg="#f0e8f5", icon="train"),
            unsafe_allow_html=True,
        )

        st.markdown(
            '<h3 style="font-size:13px; color:#1a3a2f; margin-top:8px;">'
            '<span class="material-symbols-outlined" '
            'style="font-size:16px; vertical-align:middle; margin-right:6px;">'
            'report</span>Top 10 tronçons dégradés</h3>',
            unsafe_allow_html=True,
        )
        st.dataframe(_table_troncons_degrades(df, n=10),
                     hide_index=True, width="stretch", height=340)

    # ---------- Colonne droite : graphiques ----------
    with c_right:
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.plotly_chart(_chart_donut_etat(df),
                            width="stretch", key="ifr_donut_chart")
        with r1c2:
            st.plotly_chart(_chart_pct_bon_par_region(None, df),
                            width="stretch", key="ifr_pct_chart")

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.plotly_chart(_chart_longueur_revetement(df),
                            width="stretch", key="ifr_rev_chart")
        with r2c2:
            st.plotly_chart(_chart_classement_regions(df),
                            width="stretch", key="ifr_top_chart")

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        st.plotly_chart(_chart_fret_routier_vs_rail(df_nat),
                        width="stretch", key="ifr_fret_chart")


# ################################################################
# SOUS-ONGLET 2 — ROUTES CLASSÉES
# ################################################################
def _chart_donut_type_route(df):
    counts = df["route_type"].value_counts().reset_index()
    counts.columns = ["type", "nb"]
    fig = go.Figure(go.Pie(
        labels=counts["type"], values=counts["nb"], hole=0.55,
        marker=dict(line=dict(color="white", width=2)),
        textinfo="percent", textfont=dict(size=11, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value} tronçons<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Répartition par type de route",
                   font=dict(size=13, color="#1a3a2f")),
        height=280, margin=dict(l=10, r=10, t=40, b=10),
        showlegend=True,
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=9)),
    )
    return fig


def _chart_donut_revetement(df):
    counts = df["route_recouvrement"].value_counts().reset_index()
    counts.columns = ["rev", "nb"]
    fig = go.Figure(go.Pie(
        labels=counts["rev"], values=counts["nb"], hole=0.55,
        marker=dict(line=dict(color="white", width=2)),
        textinfo="percent", textfont=dict(size=11, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value} tronçons<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Répartition par revêtement",
                   font=dict(size=13, color="#1a3a2f")),
        height=280, margin=dict(l=10, r=10, t=40, b=10),
        showlegend=True,
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=9)),
    )
    return fig


def _chart_longueur_par_region(df):
    agg = df.groupby("region_canon")["longueur_km"].sum().reset_index()
    agg = agg.sort_values("longueur_km", ascending=False)
    fig = go.Figure(go.Bar(
        x=agg["region_canon"], y=agg["longueur_km"],
        marker_color=BLEU_CHARRON,
        text=agg["longueur_km"].round(1),
        textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>%{y:.2f} km<extra></extra>",
    ))
    layout = _base_layout("Longueur du réseau classé par région (km)")
    layout["showlegend"] = False
    fig.update_layout(**layout)
    fig.update_xaxes(tickangle=-15)
    return fig


def _chart_voies(df):
    counts = df["voies_nbr"].value_counts().sort_index().reset_index()
    counts.columns = ["voies", "nb"]
    fig = go.Figure(go.Bar(
        x=counts["voies"].astype(str), y=counts["nb"],
        marker_color=BLEU_MOYEN,
        text=counts["nb"],
        textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x} voies</b><br>%{y} tronçons<extra></extra>",
    ))
    layout = _base_layout("Répartition par nombre de voies")
    layout["showlegend"] = False
    fig.update_layout(**layout)
    fig.update_xaxes(title_text="Nombre de voies")
    return fig


def _table_top_longues(df, n=10):
    top = df.sort_values("longueur_km", ascending=False).head(n).copy()
    top["rang"] = range(1, len(top) + 1)
    out = top[["rang", "route_nom", "region_canon",
               "prefecture_canon", "longueur_km"]].copy()
    out.columns = ["#", "Route", "Région", "Préfecture", "Km"]
    out["Route"] = out["Route"].astype(str).str.slice(0, 45)
    out["Km"] = out["Km"].round(2)
    return out


def _make_map_routes(df, mode="type"):
    """Carte Folium : chaque tronçon = polyligne colorée."""
    if df.empty:
        center, zoom = [8.6, 1.0], 6
    else:
        # centroïde moyen
        all_geoms = df["geometry"].dropna()
        from src.route_utils import parse_geom
        coords = []
        for g in all_geoms.head(200):
            geom = parse_geom(g)
            if geom is not None:
                c = geom.centroid
                coords.append((c.y, c.x))
        center = [sum(c[0] for c in coords) / len(coords),
                  sum(c[1] for c in coords) / len(coords)] if coords else [8.6, 1.0]
        zoom = 7

    m = folium.Map(location=center, zoom_start=zoom,
                   tiles="OpenStreetMap", control_scale=True)

    # Palette
    if mode == "type":
        types = sorted(df["route_type"].dropna().unique())
        palette = px.colors.qualitative.Set2 + px.colors.qualitative.Set3
        color_map = {t: palette[i % len(palette)] for i, t in enumerate(types)}
    else:
        revs = sorted(df["route_recouvrement"].dropna().unique())
        palette = px.colors.qualitative.Pastel
        color_map = {r: palette[i % len(palette)] for i, r in enumerate(revs)}

    from src.route_utils import parse_geom
    for _, row in df.iterrows():
        geom = parse_geom(row["geometry"])
        if geom is None:
            continue
        key = row["route_type"] if mode == "type" else row["route_recouvrement"]
        color = color_map.get(key, "#888")
        popup = (
            f"<b>{row.get('route_nom','—')}</b><br>"
            f"<span style='font-size:11px'>"
            f"{row.get('region_canon','').title()} — "
            f"{row.get('prefecture_canon','').title()}<br>"
            f"Type : <b>{row.get('route_type','')}</b><br>"
            f"Revêtement : <b>{row.get('route_recouvrement','')}</b><br>"
            f"Longueur : <b>{row.get('longueur_km',0):.2f} km</b>"
            f"</span>"
        )
        # MultiLineString ou LineString
        if geom.geom_type == "MultiLineString":
            for line in geom.geoms:
                coords = [(y, x) for x, y in line.coords]
                folium.PolyLine(coords, color=color, weight=3, opacity=0.85,
                                popup=folium.Popup(popup, max_width=280),
                                tooltip=row.get("route_nom", "")).add_to(m)
        else:
            coords = [(y, x) for x, y in geom.coords]
            folium.PolyLine(coords, color=color, weight=3, opacity=0.85,
                            popup=folium.Popup(popup, max_width=280),
                            tooltip=row.get("route_nom", "")).add_to(m)

    return m


def render_routes_classees():
    df_full = load_routes_classees()

    c_left, c_mid, c_right = st.columns([22, 43, 35])

    # ---------- Colonne gauche : filtres + KPI ----------
    with c_left:
        st.markdown(
            '<h3 style="font-size:14px; color:#1a3a2f; margin-bottom:8px;">'
            '<span class="material-symbols-outlined" '
            'style="font-size:18px; vertical-align:middle; margin-right:6px;">'
            'filter_alt</span>Filtres</h3>',
            unsafe_allow_html=True,
        )
        regions = ["Toutes"] + sorted(df_full["region_canon"].dropna().unique().tolist())
        region = st.selectbox("Région", regions, key="rc_reg")

        df_r = df_full if region == "Toutes" else df_full[df_full["region_canon"] == region]
        prefs = ["Toutes"] + sorted(df_r["prefecture_canon"].dropna().unique().tolist())
        prefecture = st.selectbox("Préfecture", prefs, key="rc_pref")

        df_p = df_r if prefecture == "Toutes" else df_r[df_r["prefecture_canon"] == prefecture]
        comms = ["Toutes"] + sorted(df_p["commune_canon"].dropna().unique().tolist())
        commune = st.selectbox("Commune", comms, key="rc_com")

        types = sorted(df_full["route_type"].dropna().unique().tolist())
        type_sel = st.multiselect("Type", types, default=types, key="rc_type")

        revs = sorted(df_full["route_recouvrement"].dropna().unique().tolist())
        rev_sel = st.multiselect("Revêtement", revs, default=revs, key="rc_rev")

        # Application des filtres
        df = df_full.copy()
        if region != "Toutes":
            df = df[df["region_canon"] == region]
        if prefecture != "Toutes":
            df = df[df["prefecture_canon"] == prefecture]
        if commune != "Toutes":
            df = df[df["commune_canon"] == commune]
        if type_sel:
            df = df[df["route_type"].isin(type_sel)]
        if rev_sel:
            df = df[df["route_recouvrement"].isin(rev_sel)]

        # KPI
        nb_troncons = len(df)
        longueur = df["longueur_km"].sum()
        voies_moy = df["voies_nbr"].mean() if nb_troncons else 0
        top_type = df["route_type"].mode().iloc[0] if nb_troncons else "—"
        top_rev = df["route_recouvrement"].mode().iloc[0] if nb_troncons else "—"

        st.markdown(
            kpi_card(f"{nb_troncons:,}".replace(",", " "),
                     "Tronçons dans le périmètre filtré",
                     bg="#e6eff7", icon="route"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{longueur:,.0f} km".replace(",", " "),
                     "Longueur cumulée", bg="#e6f4ec", icon="straighten"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{voies_moy:.2f}", "Nombre moyen de voies",
                     bg="#fdefdd", icon="multiple_stop"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{top_type}", "Type de route dominant",
                     bg="#f0e8f5", icon="label"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{top_rev}", "Revêtement dominant",
                     bg="#fbe6e6", icon="layers"),
            unsafe_allow_html=True,
        )

    # ---------- Colonne milieu : 4 graphiques + table ----------
    with c_mid:
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.plotly_chart(_chart_donut_type_route(df),
                            width="stretch", key="rc_donut_type")
        with r1c2:
            st.plotly_chart(_chart_donut_revetement(df),
                            width="stretch", key="rc_donut_rev")

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.plotly_chart(_chart_longueur_par_region(df),
                            width="stretch", key="rc_long")
        with r2c2:
            st.plotly_chart(_chart_voies(df),
                            width="stretch", key="rc_voies")

        # ⬇️ Table déplacée ici, sous les graphiques
        st.markdown(
            '<h3 style="font-size:13px; color:#1a3a2f; margin-top:14px;">'
            '<span class="material-symbols-outlined" '
            'style="font-size:16px; vertical-align:middle; margin-right:6px;">'
            'route</span>Top 10 des routes les plus longues</h3>',
            unsafe_allow_html=True,
        )
        st.dataframe(_table_top_longues(df, n=10),
                     hide_index=True, width="stretch", height=300)

    # ---------- Colonne droite : carte avec toggle ----------
    with c_right:
        mode_vue = st.radio(
            "Vue",
            ["Type", "Revêtement"],
            horizontal=True,
            key="rc_mode_vue",
            label_visibility="collapsed",
        )
        m = _make_map_routes(df, mode="type" if mode_vue == "Type" else "revetement")
        st_folium(m, height=850, width=None, returned_objects=[])

# ================================================================
# RENDER PRINCIPAL
# ================================================================
def render():
    tab1, tab2 = st.tabs(["État du réseau routier", "Routes classées"])
    with tab1:
        render_etat_reseau()
    with tab2:
        render_routes_classees()