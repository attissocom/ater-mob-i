# Dashboard Projet ATER-MOB I

**Mobilité & Sécurité Routière au Togo — Analyse 1990-2022**

Dashboard interactif développé dans le cadre du **Data Challenge organisé par TOGO AI LAB**, dans le domaine **Administration Territoriale et Mobilité**.

🔗 **Application en ligne** : [dashboard-ater-mob-i.streamlit.app](https://dashboard-ater-mob-i.streamlit.app/)

---

## Contexte et objectifs

Le nombre de véhicules immatriculés au Togo a plus que quadruplé en vingt ans, porté par les motos. En parallèle, les accidents de la route augmentent : **7 507 accidents** et **683 morts** en 2022. Le réseau routier reste inégalement entretenu selon les régions.

Ce projet construit un **tableau de bord interactif** qui mesure l'évolution de la mobilité et de la sécurité routière, et propose des recommandations pour une mobilité plus sûre.

### Objectifs spécifiques

1. **Mobilité** — Retracer l'évolution des immatriculations (voitures, motos, poids lourds) et des permis délivrés par catégorie.
2. **Sécurité routière** — Analyser accidents, blessés et morts rapportés à la population et au parc de véhicules.
3. **Infrastructures** — Évaluer l'état du réseau routier classé par tronçon et par région.
4. **Cartographie** — Visualiser le réseau classé et les auto-écoles rapportés à la population.
5. **Recommandations** — Proposer des pistes ciblées pour améliorer la sécurité, la formation et l'entretien du réseau.

---

## Données mobilisées (8 sources ouvertes)

| Source | Contenu | Période |
|---|---|---|
| **Immatriculations** (2 bases) | Parc et flux par type de véhicule | 1990-2022 |
| **Permis de conduire** | Délivrés par catégorie (A, B, C, D, E, F) | 2007-2022 |
| **Transports terrestres** | Accidents, blessés, morts, fret, trafic | 1990-2022 |
| **Réseau routier** | État (bon/moyen/mauvais/travaux) par tronçon | 2020 |
| **Routes classées** | Géométrie, type, revêtement, voies | 2022 |
| **Auto-écoles** | 269 établissements géolocalisés | 2022 |
| **Population RGPH5** | Par région, préfecture, commune, canton | 2022 |
| **Population Banque Mondiale** | Série nationale | 1960-2025 |

---

## Stack technique

- **Python 3.12** — pandas, geopandas, shapely, rapidfuzz
- **Streamlit** — application web interactive
- **Plotly** — graphiques interactifs
- **Folium** — cartes choroplèthes et polylignes
- **Déploiement** — Streamlit Community Cloud

---

## Structure du projet
ater-mob-i/
├── app.py # Point d'entrée Streamlit
├── components/ # Sidebar, topbar, footer, page header
├── views/ # 1 fichier par onglet (7 onglets)
├── src/ # Pipeline de traitement
│ ├── config.py # Chemins, seuils, règles métier
│ ├── clean_temporal.py # Nettoyage des séries temporelles
│ ├── geo_normalize.py # Normalisation des noms géographiques
│ ├── geo_crosswalk.py # Matching hiérarchique région → commune
│ ├── indicators.py # Calcul des KPI nationaux et régionaux
│ └── dashboard_data.py # Couche d'accès aux données (cache)
├── data/
│ ├── raw/ # Données brutes (8 sources)
│ ├── processed/ # KPI et tables enrichies
│ └── mappings/ # Crosswalk géographique
├── styles/ # CSS personnalisé
└── requirements.txt

---

##  Lancement en local

```bash
# 1. Cloner le dépôt
git clone https://github.com/attissocom/ater-mob-i.git
cd ater-mob-i

# 2. Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate         # Windows
source .venv/bin/activate      # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le dashboard
streamlit run app.py
 Onglets du dashboard
Accueil — Chiffres clés et tendances structurantes

Mobilité — Immatriculations et permis par catégorie

Sécurité routière — Accidents, blessés, morts (analyse nationale)

Infrastructures & Réseau — État du réseau + routes classées + cartes

Auto-écoles — Maillage territorial, densité et cartographie

Population & territoire — Démographie et densités régionales

Recommandations — 4 leviers stratégiques priorisés
