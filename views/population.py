"""
Onglet Population & territoire : répartition démographique + densité.
"""
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

from src.dashboard_data import (
    load_geo_reference, load_areas_regions,
    load_prefectures_geojson, load_regions_geojson,
    load_pop_national,   # ⬅️ ajout
)


BLEU_CHARRON = "#1F3A5F"
VERT_TOGO    = "#0b6b3a"
ORANGE_DOUX  = "#E8A33D"
VIOLET       = "#6B3FA0"
ROUGE_BRIQUE = "#B83232"


# ============================================================
# KPI CARD
# ============================================================
def kpi_card(value, label, bg="#e6f4ec", icon="groups"):
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


def _base_layout(title, height=280):
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
def _chart_pop_region(df):
    agg = df.groupby("region", as_index=False)["population"].sum()
    agg = agg.sort_values("population", ascending=False)
    fig = go.Figure(go.Bar(
        x=agg["region"], y=agg["population"],
        marker_color=BLEU_CHARRON,
        text=agg["population"].apply(lambda x: f"{int(x):,}".replace(",", " ")),
        textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>%{y:,} hab.<extra></extra>",
    ))
    layout = _base_layout("Population par région")
    layout["showlegend"] = False
    fig.update_layout(**layout)
    fig.update_xaxes(tickangle=-15)
    fig.update_yaxes(tickformat=",")
    return fig


def _chart_top_prefectures(df, n=15):
    agg = (
        df.groupby(["prefecture", "region"], as_index=False)["population"].sum()
        .sort_values("population", ascending=False).head(n)
    )
    agg = agg.sort_values("population", ascending=True)
    fig = go.Figure(go.Bar(
        x=agg["population"], y=agg["prefecture"],
        orientation="h",
        marker_color=VIOLET,
        text=agg["population"].apply(lambda x: f"{int(x):,}".replace(",", " ")),
        textposition="outside", cliponaxis=False,
        customdata=agg["region"],
        hovertemplate="<b>%{y}</b><br>%{customdata}<br>%{x:,} hab.<extra></extra>",
    ))
    layout = _base_layout(f"Top {n} préfectures les plus peuplées")
    layout["showlegend"] = False
    fig.update_layout(**layout)
    fig.update_yaxes(tickfont=dict(size=9), autorange="reversed")
    fig.update_xaxes(tickformat=",")
    return fig


def _chart_donut_regions(df):
    agg = df.groupby("region", as_index=False)["population"].sum()
    agg = agg.sort_values("population", ascending=False)
    colors = [BLEU_CHARRON, VERT_TOGO, ORANGE_DOUX, VIOLET, ROUGE_BRIQUE]
    fig = go.Figure(go.Pie(
        labels=agg["region"], values=agg["population"], hole=0.55,
        marker=dict(colors=colors[:len(agg)], line=dict(color="white", width=2)),
        textinfo="percent", textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value:,} hab.<br>%{percent}<extra></extra>",
    ))
    total = agg["population"].sum()
    fig.update_layout(
        title=dict(text="Répartition de la population",
                   font=dict(size=13, color="#1a3a2f")),
        height=280, margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10)),
        annotations=[dict(
            text=f"<b>{int(total):,}</b><br>habitants".replace(",", " "),
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=BLEU_CHARRON),
        )],
    )
    return fig


def _chart_structure(df):
    """Barres groupées : nb préfectures / communes par région."""
    agg = df.groupby("region").agg(
        prefectures=("prefecture", "nunique"),
        communes=("commune", "nunique"),
    ).reset_index()
    agg = agg.sort_values("communes", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["region"], y=agg["prefectures"], name="Préfectures",
        marker_color=BLEU_CHARRON,
        text=agg["prefectures"], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Préfectures : %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=agg["region"], y=agg["communes"], name="Communes",
        marker_color=ORANGE_DOUX,
        text=agg["communes"], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Communes : %{y}<extra></extra>",
    ))
    layout = _base_layout("Structure administrative par région")
    layout["barmode"] = "group"
    layout["showlegend"] = True
    layout["legend"] = dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                            font=dict(size=11))
    fig.update_layout(**layout)
    fig.update_xaxes(tickangle=-15)
    return fig

def _chart_evolution_pop(df_pop):
    """Courbe d'évolution de la population nationale."""
    fig = go.Figure(go.Scatter(
        x=df_pop["annee"], y=df_pop["population"],
        mode="lines+markers",
        line=dict(color=BLEU_CHARRON, width=2.4),
        marker=dict(size=4),
        fill="tozeroy", fillcolor="rgba(31,58,95,0.10)",
        hovertemplate="<b>%{x}</b><br>%{y:,} hab.<extra></extra>",
    ))
    layout = _base_layout("Évolution de la population nationale (1960 – 2025)")
    layout["showlegend"] = False
    fig.update_layout(**layout)
    fig.update_yaxes(tickformat=",")
    return fig


# ============================================================
# TABLE
# ============================================================
def _table_regions(df, areas):
    agg = df.groupby("region").agg(
        population=("population", "sum"),
        prefectures=("prefecture", "nunique"),
        communes=("commune", "nunique"),
    ).reset_index()
    agg = agg.merge(areas, on="region", how="left")
    agg["densite"] = agg["population"] / agg["area_km2"]
    agg["part_pct"] = agg["population"] / agg["population"].sum() * 100
    agg = agg.sort_values("population", ascending=False)

    out = agg[["region", "population", "prefectures", "communes",
               "area_km2", "densite", "part_pct"]].copy()
    out.columns = ["Région", "Population", "Préf.", "Communes",
                   "Surface (km²)", "Densité", "Part (%)"]
    out["Population"] = out["Population"].apply(lambda x: f"{int(x):,}".replace(",", " "))
    out["Surface (km²)"] = out["Surface (km²)"].round(0).astype(int)
    out["Densité"] = out["Densité"].round(1)
    out["Part (%)"] = out["Part (%)"].round(1)
    return out


# ============================================================
# CARTE
# ============================================================
def _make_map(df, areas, mode="population", region_filter="Toutes"):
    """Choroplèthe des régions par population ou densité."""
    regions_gj = load_regions_geojson()

    # Agrégation par région
    agg = df.groupby("region", as_index=False)["population"].sum()
    agg = agg.merge(areas, on="region", how="left")
    agg["densite"] = agg["population"] / agg["area_km2"]

    # Centre
    center, zoom = [8.6, 1.0], 7.4

    m = folium.Map(location=center, zoom_start=zoom,
                   tiles="OpenStreetMap", control_scale=True)

    # Choroplèthe uniquement si pas de filtre régional
    if region_filter == "Toutes":
        col_name = "population" if mode == "population" else "densite"
        legend_label = ("Population (hab.)" if mode == "population"
                        else "Densité (hab./km²)")

        choropleth = folium.Choropleth(
            geo_data=regions_gj,
            name=legend_label,
            data=agg,
            columns=["region", col_name],
            key_on="feature.properties.region_canon",
            fill_color="YlOrRd" if mode == "population" else "YlGnBu",
            fill_opacity=0.75,
            line_opacity=0.5,
            line_color="#333",
            legend_name=legend_label,
            highlight=True,
            control=False,
        ).add_to(m)

        # Retirer la légende native
        for key in list(choropleth._children.keys()):
            if key.startswith("color_map"):
                del choropleth._children[key]

        # Tooltip
        gj_enriched = json.loads(json.dumps(regions_gj))
        for feat in gj_enriched["features"]:
            canon = feat["properties"]["region_canon"]
            row = agg[agg["region"] == canon]
            if len(row):
                pop = int(row["population"].iloc[0])
                dens = row["densite"].iloc[0]
                feat["properties"]["pop_label"] = f"{pop:,} hab.".replace(",", " ")
                feat["properties"]["dens_label"] = f"{dens:.1f} hab./km²"
            else:
                feat["properties"]["pop_label"] = "—"
                feat["properties"]["dens_label"] = "—"

        folium.GeoJson(
            gj_enriched,
            style_function=lambda x: {"fillColor": "transparent",
                                       "color": "transparent", "weight": 0},
            tooltip=folium.GeoJsonTooltip(
                fields=["region_canon", "pop_label", "dens_label"],
                aliases=["Région :", "Population :", "Densité :"],
                localize=True, sticky=True,
                style="background:#fff; padding:8px; border-radius:6px; "
                      "font-family:Arial; font-size:12px;",
            ),
        ).add_to(m)

        # Légende custom
        legend_html = f"""
        <div style="position: fixed; bottom: 30px; left: 30px; width: 200px;
                    background: white; border-radius: 10px; padding: 10px 12px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                    font-family: Arial, sans-serif; font-size: 11px;
                    color: #1a3a2f; z-index: 9999;">
          <div style="font-weight:700; margin-bottom:6px;">{legend_label}</div>
          <div style="display:flex; align-items:center; gap:6px;">
            <div style="width:100%; height:10px; border-radius:3px;
                        background: linear-gradient(to right,
                        {'#ffffb2, #fecc5c, #fd8d3c, #f03b20, #bd0026' if mode=='population'
                         else '#edf8fb, #b2e2e2, #66c2a4, #2ca25f, #006d2c'});"></div>
          </div>
          <div style="display:flex; justify-content:space-between;
                      margin-top:4px; font-size:9.5px; color:#666;">
            <span>Faible</span><span>Élevé</span>
          </div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

    return m


# ============================================================
# RENDER
# ============================================================
def render():
    ref = load_geo_reference()
    areas = load_areas_regions()

    c_left, c_mid, c_right = st.columns([22, 43, 35])

    # ---------- Colonne gauche : filtres + KPI + table ----------
    with c_left:
        st.markdown(
            '<h3 style="font-size:14px; color:#1a3a2f; margin-bottom:8px;">'
            '<span class="material-symbols-outlined" '
            'style="font-size:18px; vertical-align:middle; margin-right:6px;">'
            'filter_alt</span>Filtres</h3>',
            unsafe_allow_html=True,
        )
        regions = ["Toutes"] + sorted(ref["region"].dropna().unique().tolist())
        region = st.selectbox("Région", regions, key="pop_reg")

        df_r = ref if region == "Toutes" else ref[ref["region"] == region]
        prefs = ["Toutes"] + sorted(df_r["prefecture"].dropna().unique().tolist())
        prefecture = st.selectbox("Préfecture", prefs, key="pop_pref")

        df_p = df_r if prefecture == "Toutes" else df_r[df_r["prefecture"] == prefecture]
        comms = ["Toutes"] + sorted(df_p["commune"].dropna().unique().tolist())
        commune = st.selectbox("Commune", comms, key="pop_com")

        # Application
        df = ref.copy()
        if region != "Toutes":
            df = df[df["region"] == region]
        if prefecture != "Toutes":
            df = df[df["prefecture"] == prefecture]
        if commune != "Toutes":
            df = df[df["commune"] == commune]

        # KPI
        total_pop = int(df["population"].sum())
        nb_pref = df["prefecture"].nunique()
        nb_com = df["commune"].nunique()

        # Région la plus peuplée (national)
        top_region = (
            ref.groupby("region")["population"].sum()
            .sort_values(ascending=False)
        )
        top_region_name = top_region.index[0].title() if len(top_region) else "—"
        top_region_pop = int(top_region.iloc[0]) if len(top_region) else 0

        # Densité moyenne de la zone filtrée
        if commune != "Toutes":
            # Pas d'aire précise au niveau commune → on affiche n/a
            dens_moy = None
        elif prefecture != "Toutes":
            areas_pref = pd.read_csv(
                __import__("src.config", fromlist=["PROCESSED_DIR"]).PROCESSED_DIR
                / "areas_prefectures.csv"
            )
            pref_area = areas_pref[areas_pref["prefecture"] == prefecture]["area_km2"].sum()
            dens_moy = total_pop / pref_area if pref_area else None
        elif region != "Toutes":
            reg_area = areas[areas["region"] == region]["area_km2"].sum()
            dens_moy = total_pop / reg_area if reg_area else None
        else:
            total_area = areas["area_km2"].sum()
            dens_moy = total_pop / total_area if total_area else None

        st.markdown(
            kpi_card(f"{total_pop:,}".replace(",", " "),
                     "Population totale", bg="#e6eff7", icon="groups"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{nb_pref}", "Préfectures",
                     bg="#e6f4ec", icon="location_city"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{nb_com}", "Communes",
                     bg="#fdefdd", icon="holiday_village"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{top_region_name}",
                     f"Région la plus peuplée<br>({top_region_pop:,} hab.)".replace(",", " "),
                     bg="#f0e8f5", icon="star"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{dens_moy:.1f} hab./km²" if dens_moy else "n/a",
                     "Densité moyenne", bg="#fbe6e6", icon="analytics"),
            unsafe_allow_html=True,
        )

        st.markdown(
            '<h3 style="font-size:13px; color:#1a3a2f; margin-top:8px;">'
            '<span class="material-symbols-outlined" '
            'style="font-size:16px; vertical-align:middle; margin-right:6px;">'
            'bar_chart</span>Classement des régions</h3>',
            unsafe_allow_html=True,
        )
        st.dataframe(_table_regions(ref, areas),
                     hide_index=True, width="stretch", height=280)

    # ---------- Colonne milieu : 4 graphiques ----------
    with c_mid:
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.plotly_chart(_chart_pop_region(df),
                            width="stretch", key="pop_bar_reg")
        with r1c2:
            st.plotly_chart(_chart_donut_regions(df),
                            width="stretch", key="pop_donut_reg")

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.plotly_chart(_chart_top_prefectures(df, n=15),
                            width="stretch", key="pop_top_pref")
        with r2c2:
            st.plotly_chart(_chart_structure(df),
                            width="stretch", key="pop_structure")
        
        # ⬇️ Graphique évolution population en bas pour occuper l'espace
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        df_pop = load_pop_national()
        st.plotly_chart(_chart_evolution_pop(df_pop),
                        width="stretch", key="pop_evolution")

    # ---------- Colonne droite : carte ----------
    with c_right:
        mode_vue = st.radio(
            "Vue",
            ["Population", "Densité"],
            horizontal=True,
            key="pop_mode_vue",
            label_visibility="collapsed",
        )
        m = _make_map(
            df, areas,
            mode="population" if mode_vue == "Population" else "densite",
            region_filter=region,
        )
        st_folium(m, height=850, width=None, returned_objects=[])
        