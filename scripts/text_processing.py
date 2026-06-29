import pandas as pd
from fonemas import Transcription
from silabeador import syllabify


class TextProcessing:
    @staticmethod
    def syllabify_silabeador(df: pd.DataFrame, in_column, out_column):
        def split_to_syllables(text: str):
            if " " in text:
                return [syllabify(word) for word in text.split(" ")]
            else:
                return [syllabify(text)]

        df[out_column] = df[in_column].apply(split_to_syllables)
        return df

    @staticmethod
    def get_phonetics_fonemas(df: pd.DataFrame, in_column, out_column):
        df[out_column] = df[in_column].apply(
            lambda x: " ".join(Transcription(x).phonetics.words)
        )
        return df

    @staticmethod
    def get_phonology_fonemas(df: pd.DataFrame, in_column, out_column):
        df[out_column] = df[in_column].apply(
            lambda x: " ".join(Transcription(x).phonology.words)
        )
        return df

    @staticmethod
    def get_phonology_syllables_fonemas(df: pd.DataFrame, in_column, out_column):
        df[out_column] = df[in_column].apply(
            lambda x: Transcription(x).phonology.syllables
        )
        return df

    @staticmethod
    def get_phonetics_syllables_fonemas(df: pd.DataFrame, in_column, out_column):
        df[out_column] = df[in_column].apply(
            lambda x: Transcription(x).phonetics.syllables
        )
        return df
