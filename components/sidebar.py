from pathlib import Path
import streamlit as st

IMG_DIR = Path(__file__).parent.parent / "img"


def render_sidebar(pages: dict, current_page: str):
    with st.sidebar:
        # Logo
        logo_path = IMG_DIR / "logo-dashboard-ater-mob-i.png"
        if logo_path.exists():
            st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
            st.image(str(logo_path), width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)

        # Navigation par boutons
        for key, meta in pages.items():
            is_active = key == current_page
            clicked = st.button(
                meta["label"],
                key=f"nav_{key}",
                icon=f":material/{meta['icon']}:",
                type="primary" if is_active else "secondary",
                width="stretch",
            )
            if clicked and not is_active:
                st.session_state.page = key
                st.rerun()