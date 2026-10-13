"""
Normalisation des noms géographiques (régions, préfectures, communes, cantons).
Utilisée avant tout fuzzy matching pour éliminer les variations d'écriture.
"""
import re
import unicodedata
from typing import Optional


# Préfixes parasites fréquents à retirer ("Préfecture de X", "Commune d'Y", ...)
_PARASITE_PREFIXES = [
    r"^prefecture\s+(de\s+|d['\s])",
    r"^commune\s+(de\s+|d['\s])",
    r"^canton\s+(de\s+|d['\s])",
    r"^region\s+(de\s+|d['\s])",
    r"^pref\s+(de\s+|d['\s])",
    r"^comm\s+(de\s+|d['\s])",
]

# Caractères à remplacer par un espace (tirets, apostrophes, ponctuation légère)
_PUNCT_PATTERN = re.compile(r"[-'’`.,()\[\]{}/\\_]")

# Espaces multiples
_MULTISPACE = re.compile(r"\s+")


def strip_accents(text: str) -> str:
    """Retire les accents (é → e, ô → o, etc.)."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_name(name: Optional[str]) -> str:
    """
    Normalise un nom géographique :
    - minuscules
    - suppression des accents
    - remplacement des tirets/apostrophes/ponctuation par un espace
    - suppression des préfixes parasites
    - compression des espaces multiples
    """
    if name is None:
        return ""
    s = str(name).strip()
    if not s or s.lower() in {"nan", "none"}:
        return ""

    s = s.lower()
    s = strip_accents(s)
    s = _PUNCT_PATTERN.sub(" ", s)

    # Supprime les préfixes parasites (peut boucler si double préfixe)
    changed = True
    while changed:
        changed = False
        for pat in _PARASITE_PREFIXES:
            new_s = re.sub(pat, "", s)
            if new_s != s:
                s = new_s
                changed = True

    s = _MULTISPACE.sub(" ", s).strip()
    return s


def normalize_series(series):
    """Applique normalize_name à une Series pandas."""
    return series.astype(str).map(normalize_name)


# ---------- Règle spéciale Grand Lomé → Maritime ----------
from src.config import GRAND_LOME_ALIASES, GRAND_LOME_TARGET


def apply_grand_lome_rule(region_value: Optional[str]) -> Optional[str]:
    """
    Si la région vaut 'Grand Lomé' (ou variante), renvoie 'maritime'.
    Sinon renvoie la valeur d'origine.
    """
    if region_value is None:
        return None
    norm = normalize_name(region_value)
    if norm in GRAND_LOME_ALIASES:
        return GRAND_LOME_TARGET
    return region_value