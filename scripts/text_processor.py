from fonemas import Transcription


class TextProcessor:
    """
    Converts raw text into phonetic syllables.
    """

    def text_to_words(self, text: str) -> list[str]:
        return text.split()

    def words_to_syllables(self, words: list[str]) -> list[list[str]]:
        return [Transcription(word).phonology.syllables for word in words]
