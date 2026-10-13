import streamlit as st


def placeholder(title: str):
    """Gabarit vide commun, en attendant l'intégration des données."""
    st.markdown(
        f'<div class="content-placeholder">'
        f"<strong>Contenu à venir</strong><br>"
        f"Cette section accueillera les KPI, graphiques et cartes "
        f"propres à l'onglet <em>{title}</em>."
        f"</div>",
        unsafe_allow_html=True,
    )