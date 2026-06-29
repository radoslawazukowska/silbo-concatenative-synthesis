"""
Maps Spanish phonemes to the six silfateo classes of Silbo Gomero.

Each Spanish phoneme is collapsed into one of six whistled classes
(two vowel classes and four consonant classes), reflecting the reduced
sound inventory of Silbo. Note that /ʝ/ is used for both "y" and "ll",
as this distinction does not exist in Canarian Spanish.
"""

import pandas as pd

from config import SYLLABLES_CSV

# Spanish phonemes grouped into the six silfateo classes
SILFATEO_CLASSES = {
    "I": "iej",
    "A": "aouw",
    "CH": "ʧtsθ",
    "K": "pk",
    "Y": "dnɲlʎʝrɾ",
    "G": "bfmgx",
}

# Per-character translation table (phoneme -> silfateo class)
_CHAR_TO_CLASS = {
    char: group for group, chars in SILFATEO_CLASSES.items() for char in chars
}
_TRANS_TABLE = str.maketrans(_CHAR_TO_CLASS)


def df_to_silfateo(df: pd.DataFrame, in_column: str, out_column: str) -> pd.DataFrame:
    """Add a silfateo column by translating the phonemized syllables in `in_column`."""
    df[out_column] = df[in_column].str.lower().str.translate(_TRANS_TABLE)
    return df


def str_to_silfateo(text: str) -> str | None:
    """Translate a single phonemized string into its silfateo form."""
    if text is None:
        return None
    return text.translate(_TRANS_TABLE)

def add_silfateo_column():
    syl_df = pd.read_csv(SYLLABLES_CSV, keep_default_na=False)
    syl_df = df_to_silfateo(syl_df, "syllable", "silfateo")
    syl_df.to_csv(SYLLABLES_CSV, index=False)


if __name__ == "__main__":
    add_silfateo_column()
