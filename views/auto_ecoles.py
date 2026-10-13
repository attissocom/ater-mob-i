"""
Onglet Auto-écoles : répartition territoriale + densité + carte.
"""
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from src.dashboard_data import (
    load_auto_ecoles, load_geo_reference,
    filter_auto_ecoles, get_population_by_level, count_by_level,
)

# ---------- Palette ----------
VERT      = "#38979A"
VERT_L    = "#d6f5e3"
BLEU      = "#2b5d8c"
BLEU_CHARRON = "#6384B1F2"    # ⬅️ nouvelle couleur
ROUGE     = "#c0392b"
JAUNE     = "#f4c20d"
ORANGE    = "#e67e22"
PALETTE_AGREG = {"Agréée": VERT, "Non agréée": ORANGE}


# ============================================================
# KPI CARD HTML
# ============================================================
def kpi_card(value, label, bg="#e6f4ec", icon="school"):
    """
    Carte KPI style PRISE II :
    - valeur en NOIR
    - label Arial 14px gris foncé
    - icône Material à droite en bleu charron
    - pas de bordure
    """
    return f"""
    <div style="background:{bg}; border-radius:12px; padding:16px 18px;
                margin-bottom:14px; position:relative; min-height:88px;
                box-shadow:0 1px 2px rgba(0,0,0,0.03);">
      <div style="font-family:Arial, sans-serif; font-size:24px; font-weight:700;
                  color:#000000; line-height:1.1; letter-spacing:-0.3px;">{value}</div>
      <div style="font-family:Arial, sans-serif; font-size:14px; color:#3a4a44;
                  margin-top:6px; line-height:1.4; padding-right:48px;">{label}</div>
      <div style="position:absolute; right:16px; top:50%;
                  transform:translateY(-50%); color:#1F3A5F;">
        <span class="material-symbols-outlined" style="font-size:30px;">{icon}</span>
      </div>
    </div>
    """

# ============================================================
# GRAPHIQUES
# ============================================================
def make_dynamic_bar(df_filt, region, prefecture, ref):
    """Barres dynamiques : région → préfecture → commune."""
    if region == "Toutes":
        level = "region"
        title = "Répartition des auto-écoles par région"
    elif prefecture == "Toutes":
        level = "prefecture"
        title = f"Répartition des auto-écoles par préfecture — {region.title()}"
    else:
        level = "commune"
        title = f"Répartition des auto-écoles par commune — {prefecture.title()}"

    counts = count_by_level(df_filt, level).sort_values("nb", ascending=False)

    fig = px.bar(
        counts, x=level, y="nb",
        text="nb",
        color_discrete_sequence=[BLEU_CHARRON],   # ⬅️
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#1a3a2f")),
        height=270, margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis_title=None, yaxis_title=None,
        xaxis=dict(tickfont=dict(size=11), tickangle=-25),
        yaxis=dict(gridcolor="#eef2ef", tickfont=dict(size=11)),
        showlegend=False,
    )
    return fig


def make_ratio_chart(df_filt, region, ref):
    """Barres horizontales : ratio auto-écoles / 100k hab (région ou préfecture)."""
    if region == "Toutes":
        level = "region"
        title = "Auto-écoles pour 100 000 habitants — par région"
        pop = get_population_by_level(ref, "region")
        key = "region"
    else:
        level = "prefecture"
        title = f"Auto-écoles pour 100 000 habitants — préfectures de {region.title()}"
        pop = get_population_by_level(ref, "prefecture")
        pop = pop[pop["region"] == region][["prefecture", "population"]]
        key = "prefecture"

    counts = count_by_level(df_filt, level)
    merged = counts.merge(
        pop.rename(columns={key: level}) if key != level else pop,
        on=level, how="left",
    )
    merged["ratio"] = merged["nb"] / merged["population"] * 100_000
    merged = merged.sort_values("ratio", ascending=True)

    national_avg = df_filt.shape[0] / ref["population"].sum() * 100_000

    colors = [ROUGE if r < national_avg else BLEU_CHARRON for r in merged["ratio"]]
    
    fig = go.Figure(go.Bar(
        x=merged["ratio"], y=merged[level],
        orientation="h",
        marker=dict(color=colors),
        text=merged["ratio"].round(2),
        textposition="outside",
        cliponaxis=False,
    ))
    fig.add_vline(
        x=national_avg, line_dash="dash", line_color="#888",
        annotation_text=f"Moy. nat. {national_avg:.2f}",
        annotation_position="top right",
        annotation_font_size=10,
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#1a3a2f")),
        height=270, margin=dict(l=10, r=40, t=40, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis_title=None, yaxis_title=None,
        xaxis=dict(gridcolor="#eef2ef"),
        yaxis=dict(tickfont=dict(size=11)),
        showlegend=False,
    )
    return fig


def make_donut(df_filt):
    """Anneau : répartition par statut d'agrégation."""
    counts = df_filt.groupby("agregation").size().reset_index(name="nb")
    fig = px.pie(
        counts, names="agregation", values="nb",
        hole=0.55,
        color="agregation",
        color_discrete_map=PALETTE_AGREG,
    )
    fig.update_traces(
        textinfo="percent",
        textfont=dict(size=12, color="white"),
        marker=dict(line=dict(color="white", width=2)),
    )
    total = counts["nb"].sum()
    fig.update_layout(
        title=dict(text="Répartition par statut d'agrégation",
                   font=dict(size=14, color="#1a3a2f")),
        height=270, margin=dict(l=10, r=10, t=40, b=10),
        showlegend=True,
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=11)),
        annotations=[dict(
            text=f"<b>{total}</b><br><span style='font-size:10px'>auto-écoles</span>",
            x=0.5, y=0.5, showarrow=False, font=dict(size=14, color=VERT),
        )],
    )
    return fig


# ============================================================
# CARTE FOLIUM
# ============================================================
def make_map(df_filt, ref, region_filter="Toutes"):
    """
    Carte Folium avec :
    - choroplèthe des régions par ratio auto-écoles / 100k hab
      (rouge = besoin urgent, vert = bien desservi)
    - marqueurs groupés des auto-écoles filtrées
    - légende et contrôle de couches repositionnés pour ne pas gêner
    """
    from src.dashboard_data import load_regions_geojson, get_population_by_level

    regions_gj = load_regions_geojson()

    # Centre et zoom selon filtre
    if df_filt.empty:
        center, zoom = [8.6, 1.0], 6
    else:
        center = [df_filt["lat"].mean(), df_filt["lon"].mean()]
        zoom = 8 if df_filt.shape[0] < 30 else 7

    m = folium.Map(
        location=center, zoom_start=zoom,
        tiles="OpenStreetMap", control_scale=True,
        zoom_control=True,
    )

    # ---------- CHOROPLÈTHE (uniquement si aucun filtre régional) ----------
    if region_filter == "Toutes":
        # 1) Compter les auto-écoles par région
        counts = df_filt.groupby("region_canon").size().reset_index(name="nb")

        # 2) Joindre la population
        pop_reg = get_population_by_level(ref, "region")
        counts = counts.merge(
            pop_reg, left_on="region_canon", right_on="region", how="left"
        )

        # 3) Ratio pour 100k hab
        counts["ratio"] = counts["nb"] / counts["population"] * 100_000

        # 4) Choroplèthe avec échelle divergente RdYlGn
        choropleth = folium.Choropleth(
            geo_data=regions_gj,
            name="Besoin en auto-écoles",
            data=counts,
            columns=["region_canon", "ratio"],
            key_on="feature.properties.region_canon",
            fill_color="RdYlGn",
            fill_opacity=0.75,
            line_opacity=0.5,
            line_color="#333333",
            threshold_scale=[0.5, 1.0, 2.0, 4.0, 6.5],  # 🔴🟠🟡🟢🟢
            legend_name="Auto-écoles pour 100 000 habitants",
            highlight=True,
            control=False,       # ⬅️ retire du menu de couches
        ).add_to(m)

        # 5) SUPPRIMER la légende native (qui traîne en haut à gauche)
        for key in list(choropleth._children.keys()):
            if key.startswith("color_map"):
                del choropleth._children[key]

        # 6) Tooltip enrichi au survol d'une région
        regions_gj_enriched = json.loads(json.dumps(regions_gj))  # deep copy
        for feat in regions_gj_enriched["features"]:
            canon = feat["properties"]["region_canon"]
            row = counts[counts["region_canon"] == canon]
            if len(row):
                nb = int(row["nb"].iloc[0])
                ratio = row["ratio"].iloc[0]
                feat["properties"]["nb_label"] = f"{nb} auto-écoles"
                feat["properties"]["ratio_label"] = f"{ratio:.2f} / 100 000 hab."
            else:
                feat["properties"]["nb_label"] = "—"
                feat["properties"]["ratio_label"] = "—"

        folium.GeoJson(
            regions_gj_enriched,
            name="Informations régions",
            style_function=lambda x: {
                "fillColor": "transparent",
                "color": "transparent",
                "weight": 0,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["region_canon", "nb_label", "ratio_label"],
                aliases=["Région :", "Équipement :", "Densité :"],
                localize=True,
                sticky=True,
                style="background:#fff; padding:8px; border-radius:6px; "
                      "font-family:Arial; font-size:12px;",
            ),
        ).add_to(m)

        # 7) LÉGENDE CUSTOM compacte, en bas à gauche
        legend_html = """
        <div style="
            position: fixed;
            bottom: 30px; left: 30px;
            width: 220px;
            background: white;
            border-radius: 10px;
            padding: 10px 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            font-family: Arial, sans-serif;
            font-size: 11px;
            color: #1a3a2f;
            z-index: 9999;
        ">
          <div style="font-weight:700; margin-bottom:6px; font-size:11.5px;">
            Auto-écoles / 100 000 hab.
          </div>
          <div style="display:flex; align-items:center; gap:6px; margin:3px 0;">
            <span style="display:inline-block; width:20px; height:12px;
                         background:#a50026; border-radius:2px;"></span>
            <span>&lt; 0.5 — Critique</span>
          </div>
          <div style="display:flex; align-items:center; gap:6px; margin:3px 0;">
            <span style="display:inline-block; width:20px; height:12px;
                         background:#f46d43; border-radius:2px;"></span>
            <span>0.5 – 1.0 — Urgent</span>
          </div>
          <div style="display:flex; align-items:center; gap:6px; margin:3px 0;">
            <span style="display:inline-block; width:20px; height:12px;
                         background:#fee08b; border-radius:2px;"></span>
            <span>1.0 – 2.0 — Insuffisant</span>
          </div>
          <div style="display:flex; align-items:center; gap:6px; margin:3px 0;">
            <span style="display:inline-block; width:20px; height:12px;
                         background:#66bd63; border-radius:2px;"></span>
            <span>2.0 – 4.0 — Correct</span>
          </div>
          <div style="display:flex; align-items:center; gap:6px; margin:3px 0;">
            <span style="display:inline-block; width:20px; height:12px;
                         background:#006837; border-radius:2px;"></span>
            <span>&gt; 4.0 — Bon</span>
          </div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

    # ---------- MARQUEURS AUTO-ÉCOLES ----------
    cluster = MarkerCluster(name="Auto-écoles").add_to(m)

    for _, row in df_filt.dropna(subset=["lat", "lon"]).iterrows():
        color = PALETTE_AGREG.get(row.get("agregation", ""), VERT)
        popup_html = (
            f"<b>{row.get('nom_etablissement','—')}</b><br>"
            f"<span style='font-size:11px'>"
            f"{row.get('commune_canon','').title()} — "
            f"{row.get('prefecture_canon','').title()}<br>"
            f"<i>{row.get('agregation','')}</i>"
            f"</span>"
        )
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5,
            color=color, fill=True, fill_color=color, fill_opacity=0.75,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row.get("nom_etablissement", ""),
        ).add_to(cluster)

    # ---------- CONTRÔLE DES COUCHES (replié, en bas à droite) ----------
    folium.LayerControl(
        collapsed=True,
        position="bottomright",
        autoZIndex=True,
    ).add_to(m)

    return m


# ============================================================
# TOP TABLE
# ============================================================
def make_bottom_table(df, n=10):
    """Préfectures avec le MOINS d'auto-écoles (les moins dotées)."""
    counts = (
        df.groupby(["prefecture_canon", "region_canon"])
        .size().reset_index(name="nb")
        .sort_values("nb", ascending=True)
        .head(n)
    )
    counts["rang"] = range(1, len(counts) + 1)
    counts = counts[["rang", "prefecture_canon", "region_canon", "nb"]]
    counts.columns = ["#", "Préfecture", "Région", "Nb"]
    return counts


# ============================================================
# RENDER PRINCIPAL
# ============================================================
def render():
    df = load_auto_ecoles()
    ref = load_geo_reference()

    # ---------- FILTRES CASCADANTS ----------
    regions = ["Toutes"] + sorted(df["region_canon"].dropna().unique())
    fc1, fc2, fc3, _ = st.columns([3, 3, 3, 1])
    region = fc1.selectbox("Région", regions, key="ae_region")

    df_reg = df if region == "Toutes" else df[df["region_canon"] == region]
    prefs = ["Toutes"] + sorted(df_reg["prefecture_canon"].dropna().unique())
    prefecture = fc2.selectbox("Préfecture", prefs, key="ae_prefecture")

    df_pref = df_reg if prefecture == "Toutes" else df_reg[df_reg["prefecture_canon"] == prefecture]
    comms = ["Toutes"] + sorted(df_pref["commune_canon"].dropna().unique())
    commune = fc3.selectbox("Commune", comms, key="ae_commune")

    # ---------- APPLICATION FILTRES ----------
    df_filt = filter_auto_ecoles(df, region, prefecture, commune)

    # ---------- KPI (1-3 nationaux, 4-5 réactifs) ----------
        # ---------- KPI ----------
    total_nat = len(df)

    # Région la mieux dotée
    top_reg_ser = df.groupby("region_canon").size().sort_values(ascending=False)
    top_region_name = top_reg_ser.index[0].title() if len(top_reg_ser) else "—"
    top_region_nb = int(top_reg_ser.iloc[0]) if len(top_reg_ser) else 0

    # Préfecture la mieux dotée (Golfe inclus)
    top_pref_ser = df.groupby("prefecture_canon").size().sort_values(ascending=False)
    top_pref_name = top_pref_ser.index[0].title() if len(top_pref_ser) else "—"
    top_pref_nb = int(top_pref_ser.iloc[0]) if len(top_pref_ser) else 0

    # Population de la zone filtrée
    if commune != "Toutes":
        pop_filt = ref[ref["commune"] == commune]["population"].sum()
        zone_label = f"commune de {commune.title()}"
    elif prefecture != "Toutes":
        pop_filt = ref[ref["prefecture"] == prefecture]["population"].sum()
        zone_label = f"préfecture de {prefecture.title()}"
    elif region != "Toutes":
        pop_filt = ref[ref["region"] == region]["population"].sum()
        zone_label = f"région {region.title()}"
    else:
        pop_filt = ref["population"].sum()
        zone_label = "national"

    # Ratio 4 : auto-écoles / 100k hab (zone filtrée)
    ratio_100k = (len(df_filt) / pop_filt * 100_000) if pop_filt else 0

    # Ratio 5 : 1 auto-école pour X habitants (zone filtrée)
    un_pour_x = int(pop_filt / len(df_filt)) if len(df_filt) else 0

    # ---------- LAYOUT 3 COLONNES ----------
    c_left, c_mid, c_right = st.columns([22, 48, 30])

    # ============ COLONNE GAUCHE ============
    with c_left:
        st.markdown(
            kpi_card(f"{total_nat}", "Auto-écoles recensées (national)",
                     bg="#e6f4ec", icon="school"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{top_region_name}",
                     f"Région la mieux dotée<br>({top_region_nb} auto-écoles)",
                     bg="#e0ecf7", icon="location_on"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{top_pref_name}",
                     f"Préfecture la mieux dotée<br>({top_pref_nb} auto-écoles)",
                     bg="#fdefdd", icon="military_tech"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"{ratio_100k:.2f}",
                     f"Auto-écoles pour 100 000 habitants<br>"
                     f"<span style='font-size:12px;color:#6b7f76;'>Zone : {zone_label}</span>",
                     bg="#f0e8f5", icon="analytics"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_card(f"1 / {un_pour_x:,}".replace(",", " "),
                     f"1 auto-école pour X habitants<br>"
                     f"<span style='font-size:12px;color:#6b7f76;'>Zone : {zone_label}</span>",
                     bg="#fbe6e6", icon="groups"),
            unsafe_allow_html=True,
        )
        
        st.markdown(
            '<h3 style="font-size:15px; color:#1a3a2f; margin-top:8px;">'
            '<span class="material-symbols-outlined" '
            'style="font-size:18px; vertical-align:middle; margin-right:6px;">'
            'trending_down</span>Préfectures les moins dotées</h3>',
            unsafe_allow_html=True,
        )
        bottom = make_bottom_table(df, n=10)
        st.dataframe(bottom, hide_index=True, use_container_width=True, height=340)

# ============ COLONNE MILIEU ============
    with c_mid:
        fig1 = make_dynamic_bar(df_filt, region, prefecture, ref)
        st.plotly_chart(fig1, use_container_width=True, key="ae_bar")

        fig2 = make_ratio_chart(df_filt, region, ref)
        st.plotly_chart(fig2, use_container_width=True, key="ae_ratio")

        fig3 = make_donut(df_filt)
        st.plotly_chart(fig3, use_container_width=True, key="ae_donut")

        # ============ COLONNE DROITE ============
        with c_right:
            st.markdown(
                '<h3 style="font-size:15px; color:#1a3a2f;">'
                '<span class="material-symbols-outlined" '
                'style="font-size:20px; vertical-align:middle; margin-right:6px;">'
                'map</span>'
                f'Carte des auto-écoles '
                f'<span style="font-size:12px;color:#6b7f76;font-weight:400;">'
                f'({len(df_filt)} sur {total_nat})</span>'
                '</h3>',
                unsafe_allow_html=True,
            )
            carte = make_map(df_filt, ref, region_filter=region)
            st_folium(carte, height=850, width=None, returned_objects=[])