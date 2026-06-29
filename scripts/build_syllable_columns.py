import pandas as pd
from text_processing import TextProcessing
from config import PROCESSED_WORDS_DIR, TRANSC_CSV

transc_words_path = TRANSC_CSV


def add_syllables(in_path, out_path, input_column):
    df = pd.read_csv(in_path)
    df = TextProcessing.syllabify_silabeador(df, input_column, "syllables")
    df.to_csv(out_path, index=False)


def add_phoneme_syllables(in_path, out_path, input_column):
    df = pd.read_csv(in_path)
    df = TextProcessing.get_phonology_fonemas(df, input_column, "fonemas_pl")
    df = TextProcessing.get_phonology_syllables_fonemas(
        df, input_column, "fonemas_pl_syl"
    )
    df.to_csv(out_path, index=False)

def build_syllable_columns():
    input_column = "transcription"
    add_syllables(TRANSC_CSV, TRANSC_CSV, input_column)
    add_phoneme_syllables(TRANSC_CSV, TRANSC_CSV, input_column)


if __name__ == "__main__":
    build_syllable_columns()
    
