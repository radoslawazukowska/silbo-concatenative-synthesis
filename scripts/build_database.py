"""
Build the syllable-unit database for Silbo Gomero concatenative synthesis.

Assumes the SLR137 'words' subset has been downloaded and placed under
data/unprocessed/words/ (see README). Runs the full preparation pipeline
end to end and writes the unit database to data/syllables/words-processed/.
"""

import os
import shutil

from config import TRANSC_CSV, UNPROCESSED_TRANSC_CSV, PROCESSED_WORDS_CLIPS, SYLLABLE_AUDIO_DIR, SYLLABLE_AUDIO_CLIPS_DIR
from audio_processing import clean_audio
from build_syllable_columns import build_syllable_columns
from audio_syllables_splitting import build_units
from postprocess_database import enrich_database
from silfateo import add_silfateo_column


def main():
    os.makedirs(os.path.dirname(TRANSC_CSV), exist_ok=True)
    os.makedirs(PROCESSED_WORDS_CLIPS, exist_ok=True)
    os.makedirs(SYLLABLE_AUDIO_DIR, exist_ok=True)
    os.makedirs(SYLLABLE_AUDIO_CLIPS_DIR, exist_ok=True)

    print("[1/5] Cleaning audio (noise reduction and filtering)...")
    clean_audio()

    print("[2/5] Adding phonemic and syllabic transcriptions...")
    shutil.copy(UNPROCESSED_TRANSC_CSV, TRANSC_CSV)
    build_syllable_columns()

    print("[3/5] Splitting recordings into syllable units...")
    build_units()

    print("[4/5] Computing unit metadata (duration, stress, position, speaker)...")
    enrich_database()

    print("[5/5] Adding silfateo sound-class mapping...")
    add_silfateo_column()

    print("Done. Unit database written to the syllable output directory.")


if __name__ == "__main__":
    main()
