import streamlit as st


def render_page_header(title: str, description: str):
    """Bandeau titre au-dessus du contenu : nom de l'onglet + description."""
    st.markdown(
        f'<div class="page-header">'
        f'  <div class="page-header-title">{title}</div>'
        f'  <div class="page-header-desc">{description}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )