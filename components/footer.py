from pathlib import Path
import streamlit as st

IMG_DIR = Path(__file__).parent.parent / "img"


def render_footer():
    """Footer : Blason (gauche) + MENTD + texte (droite) + crédit design centré."""
    st.markdown('<hr class="footer-hr">', unsafe_allow_html=True)

    col_left, col_mid, col_right = st.columns([1, 3, 6], vertical_alignment="center")

    with col_left:
        blason = IMG_DIR / "Blason-rt.png"
        if blason.exists():
            st.image(str(blason), width=55)

    with col_right:
        c_img, c_txt = st.columns([1, 6], vertical_alignment="center")
        with c_img:
            mentd = IMG_DIR / "MENTD.jpg"
            if mentd.exists():
                st.image(str(mentd), width=65)
        with c_txt:
            st.markdown(
                '<div class="footer-text">'
                "<strong>Ministère de l'Économie Numérique et de la Transformation Digitale</strong>"
                "<br><span>République Togolaise</span>"
                "</div>",
                unsafe_allow_html=True,
            )

    # ---------- Crédit design (centré, discret) ----------
    st.markdown(
        '<div style="text-align:center; margin-top:18px; padding-top:12px; '
        'border-top:1px solid #eef2ef; '
        "font-family:Arial, sans-serif; font-size:11.5px; color:#8b949e; "
        'letter-spacing:0.3px;">'
        '<span class="material-symbols-outlined" '
        'style="font-size:13px; vertical-align:middle; margin-right:4px; '
        'color:#6b7f76;">brush</span>'
        'Design by <a href="mailto:kmoiseattisso@gmail.com" '
        'style="color:#0b6b3a; text-decoration:none; font-weight:600;">'
        '@kmoiseattisso@gmail.com</a>'
        ' <span style="color:#c0c8c4;">/</span> Data Scientist'
        '</div>',
        unsafe_allow_html=True,
    )