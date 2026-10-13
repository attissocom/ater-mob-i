"""
Onglet Recommandations : 4 recommandations stratégiques dépliables.
"""
import streamlit as st


VERT_TOGO    = "#0b6b3a"
BLEU_CHARRON = "#1F3A5F"
ROUGE_BRIQUE = "#B83232"
VIOLET       = "#6B3FA0"


# ============================================================
# CSS pour les cartes dépliables
# ============================================================
_CSS = """
<style>
details.reco-card {
    transition: box-shadow 0.2s ease;
}
details.reco-card:hover {
    box-shadow: 0 4px 18px rgba(0,0,0,0.10);
}
details.reco-card summary {
    list-style: none;
    outline: none;
}
details.reco-card summary::-webkit-details-marker { display: none; }
details.reco-card summary::marker { display: none; }
details.reco-card[open] .reco-arrow {
    transform: rotate(180deg);
}
.reco-arrow {
    transition: transform 0.25s ease;
}
</style>
"""


# ============================================================
# CARTE RECOMMANDATION
# ============================================================
def _reco_card(numero, icon, titre, constat, accent, actions):
    actions_html = "".join(
        f"<li style='margin-bottom:8px;'>{a}</li>" for a in actions
    )

    return f"""
    <details class="reco-card" style="
        background: white;
        border-radius: 14px;
        margin-bottom: 18px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border-top: 5px solid {accent};
        overflow: hidden;
    ">
      <summary style="
        cursor: pointer;
        padding: 20px 22px;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        font-family: Arial, sans-serif;
      ">
        <div style="
            background: {accent};
            color: white;
            font-size: 17px;
            font-weight: 800;
            width: 36px; height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            margin-top: 2px;
        ">{numero}</div>
        <div style="flex: 1;">
          <div style="
              font-size: 15px;
              font-weight: 700;
              color: #1a3a2f;
              display: flex;
              align-items: center;
              gap: 8px;
              line-height: 1.3;
          ">
            <span class="material-symbols-outlined"
                  style="font-size:20px; color:{accent};">{icon}</span>
            {titre}
          </div>
          <div style="
              font-size: 12.5px;
              color: #5a6b63;
              margin-top: 6px;
              line-height: 1.5;
          ">
            {constat}
          </div>
        </div>
        <span class="material-symbols-outlined reco-arrow"
              style="font-size: 24px; color: {accent}; opacity: 0.7;
                     flex-shrink: 0; margin-top: 4px;">
          expand_more
        </span>
      </summary>
      <div style="
          padding: 18px 22px 20px 74px;
          font-family: Arial, sans-serif;
          font-size: 13px;
          color: #3a4a44;
          line-height: 1.6;
          border-top: 1px solid #eef2ef;
      ">
        <div style="
            font-weight: 700; color: {accent};
            margin-bottom: 12px; font-size: 13px;
            letter-spacing: 0.3px; text-transform: uppercase;
        ">
          <span class="material-symbols-outlined"
                style="font-size:16px; vertical-align:middle;
                       margin-right: 6px;">task_alt</span>
          Actions proposées
        </div>
        <ul style="margin: 0; padding-left: 20px; color: #3a4a44;">
          {actions_html}
        </ul>
      </div>
    </details>
    """


# ============================================================
# RENDER
# ============================================================
def render():
    # CSS local
    st.markdown(_CSS, unsafe_allow_html=True)

    # ---------- Titre de section ----------
    st.markdown(
        '<h2 style="font-family:Arial, sans-serif; font-size:22px; '
        'font-weight:700; color:#0b3d2a; margin: 4px 0 8px 0;">'
        '<span class="material-symbols-outlined" '
        'style="font-size:26px; vertical-align:middle; margin-right:8px; '
        'color:#0b6b3a;">lightbulb</span>'
        'Recommandations stratégiques</h2>'
        '<p style="font-family:Arial, sans-serif; font-size:13.5px; '
        'color:#5a6b63; margin: 0 0 22px 0; line-height:1.6; max-width:900px;">'
        'Synthèse des analyses et pistes d\'action prioritaires pour une '
        'mobilité plus sûre et un maillage territorial mieux équilibré au Togo.'
        '</p>',
        unsafe_allow_html=True,
    )

    # ---------- Carte 1 & 2 ----------
    c1, c2 = st.columns(2, gap="medium")

    with c1:
        st.markdown(
            _reco_card(
                numero="1",
                icon="school",
                titre="Rééquilibrer le maillage des auto-écoles",
                constat=(
                    "La région Maritime concentre <b>82 % des auto-écoles</b> "
                    "pour seulement <b>39 % de la population</b>. Le ratio "
                    "s'effondre ailleurs : 6,25 pour 100 000 hab. en Maritime "
                    "contre <b>0,73 dans les Plateaux</b> et 0,87 dans les Savanes."
                ),
                accent=VIOLET,
                actions=[
                    "Ouvrir <b>12 à 15 nouvelles auto-écoles</b> entre 2025 et 2027, "
                    "ciblées sur les préfectures de <b>Wawa, Agou, Kloto</b> "
                    "(Plateaux) et <b>Kpendjal, Tône</b> (Savanes).",
                    "Instaurer un <b>dispositif de bourses</b> pour les jeunes "
                    "ruraux (frais de formation 2-roues et 4-roues).",
                    "Objectif 2030 : <b>porter le ratio national à 3 auto-écoles "
                    "pour 100 000 habitants</b>, contre 1,42 aujourd'hui.",
                ],
            ),
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            _reco_card(
                numero="2",
                icon="two_wheeler",
                titre="Plan d'urgence sécurité « 2 roues »",
                constat=(
                    "Les motos représentent <b>72 % des immatriculations 2022</b> "
                    "(67 639 sur 93 770) et cette part progresse (+57 % depuis 2018). "
                    "Sur la même période, les accidents ont augmenté de <b>+29 %</b> "
                    "avec <b>683 morts</b> et <b>9 918 blessés</b> en 2022."
                ),
                accent=ROUGE_BRIQUE,
                actions=[
                    "Lancer une <b>campagne nationale de sensibilisation</b> "
                    "ciblant les conducteurs de 2 roues (radios locales, "
                    "affichage, milieu scolaire).",
                    "Distribuer <b>50 000 casques certifiés subventionnés</b> "
                    "sur 2 ans, prioritairement en zones rurales.",
                    "Renforcer la <b>formation obligatoire</b> pour la catégorie A "
                    "(permis moto) : aujourd'hui ~4 800 permis/an pour ~67 000 motos "
                    "immatriculées.",
                    "Intensifier les <b>contrôles routiers</b> sur les axes RN1, "
                    "RN4 et RN15 (radars, contrôles vitesse).",
                ],
            ),
            unsafe_allow_html=True,
        )

    # ---------- Carte 3 & 4 ----------
    c3, c4 = st.columns(2, gap="medium")

    with c3:
        st.markdown(
            _reco_card(
                numero="3",
                icon="add_road",
                titre="Programme prioritaire d'entretien du réseau",
                constat=(
                    "Sur les <b>2 198 km de routes revêtues</b>, seulement "
                    "<b>34 % sont en bon état</b>. <b>26 % (562 km) sont en mauvais état</b> "
                    "et 20 % en travaux. Sur les 1 930 km de routes en terre, "
                    "seulement 25 % sont en bon état."
                ),
                accent=BLEU_CHARRON,
                actions=[
                    "Prioriser la <b>réhabilitation des 562 km de routes revêtues "
                    "en mauvais état</b>, en ciblant les axes structurants : "
                    "<b>RN1</b> (Lomé–Kara–Dapaong), <b>RN4</b> (Lomé–Anfoin) "
                    "et <b>RN15</b> (Kpalimé–Témédja).",
                    "Créer un <b>fonds d'entretien routier pérenne</b> adossé "
                    "aux recettes de carburant.",
                    "Objectif 2030 : <b>porter la part de routes revêtues en bon "
                    "état de 34 % à 60 %</b>.",
                ],
            ),
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            _reco_card(
                numero="4",
                icon="database",
                titre="Observatoire national de la mobilité",
                constat=(
                    "Les données proviennent de sources hétérogènes avec des "
                    "écarts identifiés : <b>divergence >1 %</b> entre les deux "
                    "bases d'immatriculations, <b>absence de granularité régionale</b> "
                    "sur les accidents, année 2013 manquante pour les permis."
                ),
                accent=VERT_TOGO,
                actions=[
                    "Institutionnaliser un <b>observatoire national</b> rattaché "
                    "au Ministère chargé des Transports, alimenté annuellement par "
                    "la DGI, la Direction de la Sécurité Routière et les agences "
                    "routières.",
                    "Publier un <b>rapport annuel</b> reprenant les KPI du présent "
                    "dashboard (accidents pour 100 000 hab., taux de motorisation, "
                    "densité d'auto-écoles, état du réseau).",
                    "Ouvrir une <b>API publique</b> pour permettre aux chercheurs, "
                    "ONG et collectivités de réutiliser les données.",
                ],
            ),
            unsafe_allow_html=True,
        )

    # ---------- Bandeau de synthèse ----------
    st.markdown(
        '<div style="'
        'background: linear-gradient(135deg, #f6fbf8 0%, #eef7f1 100%);'
        'border-left: 5px solid #0b6b3a;'
        'border-radius: 12px;'
        'padding: 20px 24px;'
        'margin-top: 26px;'
        'font-family: Arial, sans-serif;'
        'font-size: 13.5px;'
        'color: #3a4a44;'
        'line-height: 1.7;'
        '">'
        '<b style="color:#0b6b3a; font-size:14.5px;">'
        '<span class="material-symbols-outlined" '
        'style="font-size:18px; vertical-align:middle; margin-right:6px;">'
        'summarize</span>'
        'Synthèse</b><br>'
        'Les quatre leviers identifiés — <b>maillage des auto-écoles</b>, '
        '<b>sécurité des 2 roues</b>, <b>entretien du réseau</b> et '
        '<b>gouvernance de la donnée</b> — sont complémentaires et '
        'conditionnent ensemble la réussite d\'une politique de mobilité '
        'sûre, inclusive et durable pour le Togo à l\'horizon 2030.'
        '</div>',
        unsafe_allow_html=True,
    )