import streamlit as st


def render_topbar(page: str):
    c1, c2, c3, c4 = st.columns([0.5, 8, 0.5, 0.5], vertical_alignment="center")

    with c1:
        if st.button("​", key="btn_menu", icon=":material/menu:",
                     help="Replier / déplier le menu"):
            st.session_state.sidebar_state = (
                "mini" if st.session_state.sidebar_state == "open" else "open"
            )
            st.rerun()

    with c2:
        st.markdown(
            '<div class="topbar-title">Administration Territoriale et Mobilité</div>',
            unsafe_allow_html=True,
        )

    with c3:
        dark = st.session_state.theme == "dark"
        icon = ":material/light_mode:" if dark else ":material/dark_mode:"
        if st.button("​", key="btn_theme", icon=icon,
                     help="Basculer le thème"):
            st.session_state.theme = "light" if dark else "dark"
            st.rerun()

    with c4:
        st.button("​", key="btn_settings", icon=":material/settings:",
                  help="Paramètres", disabled=True)