# ============================================================
# Data paths
# ============================================================

# --- Raw corpus (downloaded by the user; see README) ---
UNPROCESSED_WORDS_DIR = "data/unprocessed/words/"
UNPROCESSED_WORDS_CLIPS = UNPROCESSED_WORDS_DIR + "clips/"
UNPROCESSED_TRANSC_CSV = UNPROCESSED_WORDS_DIR + "transc.csv"

# --- Processed (denoised) word recordings ---
PROCESSED_WORDS_DIR = "data/processed/words/"
PROCESSED_WORDS_CLIPS = PROCESSED_WORDS_DIR + "clips/"
TRANSC_CSV = PROCESSED_WORDS_DIR + "transc.csv"  # master transcription table

# --- Syllable-level units (split output) ---
SYLLABLE_AUDIO_DIR = "data/syllables/words-processed/"  # syllable audio + CSVs
DESC_CSV = SYLLABLE_AUDIO_DIR + "desc.csv"  # filtered subset of transc to process
SYLLABLES_CSV = (
    SYLLABLE_AUDIO_DIR + "syllables.csv"
)  # per-syllable unit metadata (the unit DB)

# --- Generation output ---
OUTPUT_CLIPS_DIR = "output/clips/"
OUTPUT_METADATA_CSV = "output/metadata.csv"
OUTPUT_MISSING_CSV = "output/missing.csv"
TRACE_DIR = "output/traces/"


# ============================================================
# Per-speaker split parameters
# (minimum silence length in ms, silence threshold in dBFS)
# Keyed by the speaker name as it appears in the corpus 'author' column.
# ============================================================

SPEAKER_PARAMS = {
    "Ana Luz Arteaga": {"min_silence_len": 75, "silence_thresh": -13},
    "Francisco Javier Correa": {"min_silence_len": 60, "silence_thresh": -16},
    "Juan Manuel Chinea": {"min_silence_len": 66, "silence_thresh": -19},
    "Silvia Martín": {"min_silence_len": 70, "silence_thresh": -12},
}
