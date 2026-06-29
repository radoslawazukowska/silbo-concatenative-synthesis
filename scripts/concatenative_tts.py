import pandas as pd
from text_processor import TextProcessor
from syllable_resolver import SyllableResolver
from selection_policy import SelectionPolicy
from audio_synthesizer import AudioSynthesizer
from trace_logger import TraceLogger


class ConcatenativeTTS:
    """
    Coordinates the full TTS pipeline.
    """

    def __init__(self, metadata_path, root_path):
        metadata = pd.read_csv(metadata_path, keep_default_na=False)

        self.processor = TextProcessor()
        self.resolver = SyllableResolver(metadata)
        self.selector = SelectionPolicy()
        self.synth = AudioSynthesizer(root_path)
        self.logger = TraceLogger()

        self._missing_syllables_count = {}

    def get_missing_syllables_stats(self):
        return self._missing_syllables_count

    def _add_missing_syllable(self, syllable, word):
        syllable = tuple(syllable) if isinstance(syllable, list) else syllable

        if syllable not in self._missing_syllables_count:
            self._missing_syllables_count[syllable] = {"count": 0, "words": set()}

        self._missing_syllables_count[syllable]["count"] += 1
        self._missing_syllables_count[syllable]["words"].add(word)

    def generate(self, text, silence_len=0.3, rand=False):
        had_missing = 0

        words = self.processor.text_to_words(text)
        syllables_by_word = self.processor.words_to_syllables(words)

        syllable_map = self.resolver.build_cache(syllables_by_word)

        trace = []
        paths = []

        for word, syllables in zip(words, syllables_by_word):
            chosen_seq = self.selector.viterbi_select(syllables, syllable_map)

            if not chosen_seq:
                for syl in syllables:
                    self._add_missing_syllable(syl, word)
                had_missing = 1
                continue

            for pos, item in enumerate(chosen_seq):
                syl = item["syl"]
                chosen = item["selected"]
                matches = item["matches"]

                entry = syllable_map[syl]
                fallback = entry["fallback"]

                trace.append(
                    self.logger.make_entry(
                        syl, word, pos, matches, fallback, "viterbi", chosen["path"]
                    )
                )

                paths.append(chosen["path"])

            trace.append(
                self.logger.make_entry(
                    None, None, None, None, None, "silence", "<SILENCE>", "silence"
                )
            )
            paths.append("<SILENCE>")

        trace = trace[:-1] # drop the trailing silence appended after the final word

        audio, sr = self.synth.concatenate(paths, silence_len)

        return audio, sr, had_missing, trace
