"""
Génère le PowerPoint de présentation ATER-MOB I (10 slides).
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---------- Palette ----------
VERT_TOGO    = RGBColor(0x0B, 0x6B, 0x3A)
BLEU_CHARRON = RGBColor(0x1F, 0x3A, 0x5F)
ORANGE_DOUX  = RGBColor(0xE8, 0xA3, 0x3D)
ROUGE_BRIQUE = RGBColor(0xB8, 0x32, 0x32)
VIOLET       = RGBColor(0x6B, 0x3F, 0xA0)
BLANC        = RGBColor(0xFF, 0xFF, 0xFF)
GRIS_FONCE   = RGBColor(0x3A, 0x4A, 0x44)
GRIS_CLAIR   = RGBColor(0xEE, 0xF2, 0xEF)
NOIR         = RGBColor(0x00, 0x00, 0x00)

IMG_DIR = ROOT / "img" / "ppt"
OUTPUT = ROOT / "reports" / "ATER-MOB-I_presentation.pptx"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)


# ============================================================
# HELPERS
# ============================================================
def add_bg(slide, color=BLANC):
    """Fond de slide."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                                 prs.slide_width, prs.slide_height)
    bg.fill.solid(); bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    bg.shadow.inherit = False
    slide.shapes._spTree.remove(bg._element)
    slide.shapes._spTree.insert(2, bg._element)
    return bg


def add_textbox(slide, x, y, w, h, text, size=18, bold=False,
                color=NOIR, align=PP_ALIGN.LEFT, font="Arial"):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    for run in p.runs:
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = font
    return tb


def add_bullets(slide, x, y, w, h, items, size=16, color=GRIS_FONCE,
                bullet_color=VERT_TOGO, spacing=6):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "• " + item
        p.space_after = Pt(spacing)
        for run in p.runs:
            run.font.size = Pt(size)
            run.font.color.rgb = color
            run.font.name = "Arial"
    return tb


def add_rect(slide, x, y, w, h, fill, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line:
        sh.line.color.rgb = line
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def add_kpi_card(slide, x, y, w, h, value, label, accent=VERT_TOGO):
    """Carte KPI rectangulaire."""
    card = add_rect(slide, x, y, w, h, BLANC, line=GRIS_CLAIR)
    # Bande colorée en haut
    top = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(x), Inches(y),
                                  Inches(w), Inches(0.08))
    top.fill.solid(); top.fill.fore_color.rgb = accent
    top.line.fill.background()
    top.shadow.inherit = False
    # Valeur
    add_textbox(slide, x + 0.2, y + 0.25, w - 0.4, 0.6,
                value, size=26, bold=True, color=NOIR,
                align=PP_ALIGN.CENTER)
    # Label
    add_textbox(slide, x + 0.2, y + 0.95, w - 0.4, 0.8,
                label, size=11, color=GRIS_FONCE,
                align=PP_ALIGN.CENTER)


def add_slide_number(slide, n):
    add_textbox(slide, 12.3, 7.0, 1, 0.4, f"{n:02d}",
                size=11, color=GRIS_FONCE, align=PP_ALIGN.RIGHT)


def add_title_bar(slide, title, subtitle=None):
    """Barre de titre avec soulignement."""
    add_textbox(slide, 0.5, 0.35, 12, 0.7, title,
                size=26, bold=True, color=VERT_TOGO)
    # Trait sous le titre
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(0.5), Inches(1.05),
                                  Inches(1.2), Inches(0.05))
    bar.fill.solid(); bar.fill.fore_color.rgb = VERT_TOGO
    bar.line.fill.background(); bar.shadow.inherit = False

    if subtitle:
        add_textbox(slide, 0.5, 1.15, 12, 0.5, subtitle,
                    size=13, color=GRIS_FONCE)


def add_image_safe(slide, path, x, y, w=None, h=None):
    p = Path(path)
    if not p.exists():
        return False
    kwargs = {}
    if w: kwargs["width"] = Inches(w)
    if h: kwargs["height"] = Inches(h)
    slide.shapes.add_picture(str(p), Inches(x), Inches(y), **kwargs)
    return True


# ============================================================
# SLIDE 1 — COUVERTURE
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(s, BLEU_CHARRON)

# Bandeau vert vertical gauche
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                           Inches(0.4), prs.slide_height)
band.fill.solid(); band.fill.fore_color.rgb = VERT_TOGO
band.line.fill.background(); band.shadow.inherit = False

add_textbox(s, 1.5, 2.2, 10.3, 1.2, "ATER-MOB I",
            size=54, bold=True, color=BLANC, align=PP_ALIGN.CENTER)
add_textbox(s, 1.5, 3.5, 10.3, 0.6,
            "Dashboard Mobilité & Sécurité Routière au Togo",
            size=22, color=BLANC, align=PP_ALIGN.CENTER)
add_textbox(s, 1.5, 4.3, 10.3, 0.5,
            "Analyse 1990 – 2022 et recommandations stratégiques",
            size=16, color=RGBColor(0xD6, 0xF5, 0xE3),
            align=PP_ALIGN.CENTER)

# Pied de page
add_textbox(s, 1.5, 6.5, 10.3, 0.5,
            "Administration Territoriale et Mobilité  •  République Togolaise",
            size=12, color=RGBColor(0xB0, 0xC0, 0xB8),
            align=PP_ALIGN.CENTER)


# ============================================================
# SLIDE 2 — CONTEXTE
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(s)
add_title_bar(s, "Un enjeu de mobilité et de sécurité routière croissant",
              "Le Togo fait face à une transformation rapide de sa mobilité et à une accidentologie en hausse")

# 4 KPI cards en haut
kpis = [
    ("+ 4×", "de véhicules immatriculés\nen 20 ans", ORANGE_DOUX),
    ("7 507", "accidents en 2022\n(+29% vs 2018)", ROUGE_BRIQUE),
    ("26 %", "des routes revêtues\nen mauvais état", BLEU_CHARRON),
    ("82 %", "des auto-écoles dans\nla seule région Maritime", VIOLET),
]
for i, (v, l, c) in enumerate(kpis):
    add_kpi_card(s, 0.6 + i * 3.15, 2.0, 2.9, 1.9, v, l, accent=c)

# Graphique à droite (si dispo)
if not add_image_safe(s, IMG_DIR / "mob_immat.png", 0.6, 4.3, w=6.5):
    add_textbox(s, 0.6, 4.3, 6.5, 2.5,
                "[Graphique : évolution immatriculations]",
                size=12, color=GRIS_FONCE, align=PP_ALIGN.CENTER)

# Texte droite
add_bullets(s, 7.5, 4.3, 5.3, 2.5, [
    "Portée par les motos (72 % du parc en 2022)",
    "Accidents en hausse continue depuis 2018",
    "Réseau inégalement entretenu selon les régions",
    "Maillage des auto-écoles très concentré",
], size=13)


# ============================================================
# SLIDE 3 — OBJECTIFS
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(s)
add_title_bar(s, "Mesurer, comprendre, recommander",
              "Quatre objectifs structurants pour éclairer la décision publique")

objectifs = [
    ("Mobilité", "Retracer l'évolution des immatriculations (1990-2022)\net des permis délivrés par catégorie", BLEU_CHARRON, "directions_car"),
    ("Sécurité", "Analyser les accidents, blessés et morts\nrapportés à la population et au parc", ROUGE_BRIQUE, "warning"),
    ("Réseau & formation", "Évaluer l'état du réseau routier et le maillage\ndes auto-écoles par région et préfecture", VIOLET, "add_road"),
    ("Recommandations", "Proposer des pistes ciblées pour une mobilité\nplus sûre et mieux desservie", VERT_TOGO, "lightbulb"),
]
for i, (titre, desc, c, ic) in enumerate(objectifs):
    row = i // 2
    col = i % 2
    x = 0.6 + col * 6.3
    y = 2.0 + row * 2.4
    card = add_rect(s, x, y, 5.8, 2.0, BLANC, line=GRIS_CLAIR)
    # Barre latérale
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                              Inches(0.1), Inches(2.0))
    bar.fill.solid(); bar.fill.fore_color.rgb = c
    bar.line.fill.background(); bar.shadow.inherit = False
    # Numéro
    add_textbox(s, x + 0.35, y + 0.2, 0.6, 0.6,
                f"{i+1}", size=30, bold=True, color=c)
    # Titre
    add_textbox(s, x + 1.1, y + 0.25, 4.4, 0.5,
                titre, size=17, bold=True, color=GRIS_FONCE)
    # Description
    add_textbox(s, x + 1.1, y + 0.9, 4.4, 1.0,
                desc, size=12, color=GRIS_FONCE)


# ============================================================
# SLIDE 4 — MÉTHODOLOGIE
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(s)
add_title_bar(s, "Une approche data-driven à partir de 8 sources ouvertes",
              "Pipeline en 5 étapes, de la donnée brute à la décision")

# Pipeline horizontal
steps = [
    ("1. Sources", "8 bases\nbrutes", BLEU_CHARRON),
    ("2. Nettoyage", "Qualité\n& cohérence", VIOLET),
    ("3. Harmonisation", "Géo + temporel\nCrosswalk", ORANGE_DOUX),
    ("4. KPI", "30+\nindicateurs", VERT_TOGO),
    ("5. Dashboard", "Streamlit\n+ Plotly", ROUGE_BRIQUE),
]
for i, (titre, desc, c) in enumerate(steps):
    x = 0.6 + i * 2.5
    # Boîte
    box = add_rect(s, x, 2.1, 2.2, 1.8, BLANC, line=c)
    add_textbox(s, x + 0.1, 2.25, 2.0, 0.5, titre,
                size=14, bold=True, color=c, align=PP_ALIGN.CENTER)
    add_textbox(s, x + 0.1, 2.85, 2.0, 1.0, desc,
                size=11, color=GRIS_FONCE, align=PP_ALIGN.CENTER)
    # Flèche
    if i < len(steps) - 1:
        arrow = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
                                    Inches(x + 2.25), Inches(2.8),
                                    Inches(0.2), Inches(0.4))
        arrow.fill.solid(); arrow.fill.fore_color.rgb = GRIS_CLAIR
        arrow.line.fill.background(); arrow.shadow.inherit = False

# Sources en bas
add_textbox(s, 0.6, 4.3, 12, 0.4,
            "Sources mobilisées", size=15, bold=True, color=VERT_TOGO)
add_bullets(s, 0.6, 4.8, 6.0, 2.3, [
    "Immatriculations (2 bases) — 1990-2022",
    "Permis de conduire par catégorie — 2007-2022",
    "Accidents, blessés, morts — 1990-2022",
    "Réseau routier classé (état, tronçons)",
], size=12)
add_bullets(s, 6.8, 4.8, 6.0, 2.3, [
    "Routes classées (géométrie MultiLineString)",
    "Auto-écoles géolocalisées (271 établissements)",
    "Population RGPH5 (5 régions, 39 préfectures)",
    "Population Banque Mondiale — 1960-2025",
], size=12)

# Outils
add_textbox(s, 0.6, 7.0, 12, 0.4,
            "Outils : Python (pandas, geopandas) • Streamlit • Plotly • Folium",
            size=11, color=GRIS_FONCE, align=PP_ALIGN.CENTER)


# ============================================================
# SLIDE 5 — RÉSULTATS MOBILITÉ
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(s)
add_title_bar(s, "Résultats 1 — Une explosion des 2 roues",
              "Les motos dominent désormais le paysage de la mobilité togolaise")

# 3 KPI cards
kpis = [
    ("93 770", "véhicules immatriculés\nen 2022", BLEU_CHARRON),
    ("72 %", "part des 2 roues\ndans le parc 2022", ORANGE_DOUX),
    ("+57 %", "de motos immatriculées\nentre 2018 et 2022", ROUGE_BRIQUE),
]
for i, (v, l, c) in enumerate(kpis):
    add_kpi_card(s, 0.6 + i * 4.15, 1.9, 3.9, 1.8, v, l, accent=c)

# Graphique
if not add_image_safe(s, IMG_DIR / "mob_immat.png", 0.6, 4.0, w=11.8):
    add_textbox(s, 0.6, 4.0, 12, 3.0,
                "[Graphique : évolution immatriculations 1990-2022]",
                size=13, color=GRIS_FONCE, align=PP_ALIGN.CENTER)


# ============================================================
# SLIDE 6 — RÉSULTATS SÉCURITÉ
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(s)
add_title_bar(s, "Résultats 2 — Une accidentologie en hausse",
              "Une mortalité qui reste préoccupante malgré les efforts engagés")

kpis = [
    ("7 507", "accidents en 2022\n(+29 % vs 2018)", ROUGE_BRIQUE),
    ("683", "morts sur les routes\nen 2022", ROUGE_BRIQUE),
    ("9,1 %", "taux de mortalité\n(morts / accidents)", VIOLET),
    ("8,5", "morts pour 100 000 habitants", ORANGE_DOUX),
]
for i, (v, l, c) in enumerate(kpis):
    add_kpi_card(s, 0.6 + i * 3.15, 1.9, 2.9, 1.8, v, l, accent=c)

if not add_image_safe(s, IMG_DIR / "secu_accidents.png", 0.6, 4.0, w=11.8):
    add_textbox(s, 0.6, 4.0, 12, 3.0,
                "[Graphique : accidents vs morts 1990-2022]",
                size=13, color=GRIS_FONCE, align=PP_ALIGN.CENTER)


# ============================================================
# SLIDE 7 — RÉSULTATS INFRASTRUCTURES & MAILLAGE
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(s)
add_title_bar(s, "Résultats 3 — Réseau & maillage déséquilibrés",
              "Un réseau inégalement entretenu et une concentration des auto-écoles")

# Bloc gauche : réseau
add_textbox(s, 0.6, 1.9, 6.0, 0.4,
            "État du réseau routier", size=15, bold=True, color=BLEU_CHARRON)
reseau_data = [
    ("34 %", "bon état", VERT_TOGO),
    ("20 %", "en travaux", ORANGE_DOUX),
    ("26 %", "mauvais état", ROUGE_BRIQUE),
    ("20 %", "état moyen", VIOLET),
]
for i, (v, l, c) in enumerate(reseau_data):
    x = 0.6 + (i % 2) * 3.05
    y = 2.4 + (i // 2) * 1.1
    add_kpi_card(s, x, y, 2.85, 0.95, v, l, accent=c)

# Bloc droit : auto-écoles
add_textbox(s, 7.0, 1.9, 6.0, 0.4,
            "Densité d'auto-écoles pour 100 000 hab.", size=15, bold=True, color=VIOLET)
auto_data = [
    ("6,25", "Maritime", VERT_TOGO),
    ("1,51", "Centrale", ORANGE_DOUX),
    ("1,42", "Kara", ORANGE_DOUX),
    ("0,73", "Plateaux", ROUGE_BRIQUE),
]
for i, (v, l, c) in enumerate(auto_data):
    x = 7.0 + (i % 2) * 3.05
    y = 2.4 + (i // 2) * 1.1
    add_kpi_card(s, x, y, 2.85, 0.95, v, l, accent=c)

# Graphiques en bas (si dispo)
if not add_image_safe(s, IMG_DIR / "reseau_etat.png", 0.6, 4.8, w=6.0):
    add_textbox(s, 0.6, 4.8, 6.0, 2.3,
                "[Camembert : état du réseau]",
                size=11, color=GRIS_FONCE, align=PP_ALIGN.CENTER)

if not add_image_safe(s, IMG_DIR / "auto_ecoles_densite.png", 7.0, 4.8, w=6.0):
    add_textbox(s, 7.0, 4.8, 6.0, 2.3,
                "[Barres : densité auto-écoles]",
                size=11, color=GRIS_FONCE, align=PP_ALIGN.CENTER)


# ============================================================
# SLIDE 8 — SYNTHÈSE
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(s)
add_title_bar(s, "4 constats structurants",
              "Ce qu'il faut retenir de l'analyse 1990-2022")

constats = [
    ("2 roues dominantes", "72 % du parc, +57 % depuis 2018", ORANGE_DOUX, "two_wheeler"),
    ("Sécurité en dégradation", "7 507 accidents, 683 morts en 2022", ROUGE_BRIQUE, "warning"),
    ("Réseau inégalement entretenu", "26 % de routes revêtues en mauvais état", BLEU_CHARRON, "add_road"),
    ("Maillage concentré", "82 % des auto-écoles en Maritime", VIOLET, "school"),
]
for i, (titre, desc, c, ic) in enumerate(constats):
    row = i // 2; col = i % 2
    x = 0.6 + col * 6.3
    y = 2.0 + row * 2.2
    card = add_rect(s, x, y, 5.8, 1.9, BLANC, line=GRIS_CLAIR)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                              Inches(0.1), Inches(1.9))
    bar.fill.solid(); bar.fill.fore_color.rgb = c
    bar.line.fill.background(); bar.shadow.inherit = False
    add_textbox(s, x + 0.35, y + 0.25, 5.0, 0.5,
                titre, size=17, bold=True, color=c)
    add_textbox(s, x + 0.35, y + 0.95, 5.0, 0.8,
                desc, size=13, color=GRIS_FONCE)


# ============================================================
# SLIDE 9 — RECOMMANDATIONS
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(s)
add_title_bar(s, "4 leviers d'action prioritaires",
              "Des recommandations chiffrées pour une mobilité plus sûre à l'horizon 2030")

recos = [
    ("1", "Rééquilibrer le maillage des auto-écoles",
     "12 à 15 nouvelles auto-écoles en Plateaux et Savanes d'ici 2027",
     VIOLET),
    ("2", "Plan d'urgence sécurité 2 roues",
     "Campagne nationale, 50 000 casques subventionnés, contrôles renforcés",
     ROUGE_BRIQUE),
    ("3", "Programme prioritaire d'entretien",
     "562 km de routes revêtues à réhabiliter (RN1, RN4, RN15)",
     BLEU_CHARRON),
    ("4", "Observatoire national de la mobilité",
     "Institutionnaliser la collecte et la publication annuelle des KPI",
     VERT_TOGO),
]
for i, (num, titre, desc, c) in enumerate(recos):
    row = i // 2; col = i % 2
    x = 0.6 + col * 6.3
    y = 2.0 + row * 2.2
    card = add_rect(s, x, y, 5.8, 1.9, BLANC, line=GRIS_CLAIR)
    # Badge numéroté
    circle = s.shapes.add_shape(MSO_SHAPE.OVAL,
                                 Inches(x + 0.3), Inches(y + 0.3),
                                 Inches(0.7), Inches(0.7))
    circle.fill.solid(); circle.fill.fore_color.rgb = c
    circle.line.fill.background(); circle.shadow.inherit = False
    add_textbox(s, x + 0.3, y + 0.42, 0.7, 0.5, num,
                size=22, bold=True, color=BLANC, align=PP_ALIGN.CENTER)
    # Titre
    add_textbox(s, x + 1.2, y + 0.35, 4.4, 0.5,
                titre, size=15, bold=True, color=c)
    # Desc
    add_textbox(s, x + 1.2, y + 0.95, 4.4, 0.9,
                desc, size=12, color=GRIS_FONCE)


# ============================================================
# SLIDE 10 — CONCLUSION
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(s, BLEU_CHARRON)

# Bandeau vert vertical gauche
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                           Inches(0.4), prs.slide_height)
band.fill.solid(); band.fill.fore_color.rgb = VERT_TOGO
band.line.fill.background(); band.shadow.inherit = False

add_textbox(s, 0.8, 1.2, 11.8, 0.9,
            "Vers une mobilité sûre et inclusive",
            size=34, bold=True, color=BLANC, align=PP_ALIGN.CENTER)
add_textbox(s, 0.8, 2.1, 11.8, 0.5,
            "à l'horizon 2030", size=20, color=RGBColor(0xD6, 0xF5, 0xE3),
            align=PP_ALIGN.CENTER)

# 3 blocs
blocs = [
    ("Diagnostic clair",
     "La mobilité togolaise est dominée par les 2 roues\navec une accidentologie croissante"),
    ("Leviers identifiés",
     "Formation • Sécurité • Entretien • Gouvernance\nde la donnée"),
    ("Outil opérationnel",
     "Le dashboard ATER-MOB I comme support de pilotage\ncontinu pour les décideurs"),
]
for i, (titre, desc) in enumerate(blocs):
    x = 1.0 + i * 4.0
    card = add_rect(s, x, 3.2, 3.6, 2.2,
                    RGBColor(0x2A, 0x4A, 0x70), line=VERT_TOGO)
    add_textbox(s, x + 0.2, 3.4, 3.2, 0.5,
                titre, size=15, bold=True, color=RGBColor(0xD6, 0xF5, 0xE3),
                align=PP_ALIGN.CENTER)
    add_textbox(s, x + 0.2, 4.0, 3.2, 1.3,
                desc, size=11, color=BLANC, align=PP_ALIGN.CENTER)

# Merci
add_textbox(s, 0.8, 6.3, 11.8, 0.6,
            "Merci  —  Questions",
            size=22, bold=True, color=BLANC, align=PP_ALIGN.CENTER)


# ============================================================
# SAUVEGARDE
# ============================================================
prs.save(str(OUTPUT))
print(f"✅ PowerPoint généré : {OUTPUT}")
print(f"   {len(prs.slides)} slides")