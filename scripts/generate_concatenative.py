import argparse
import os

import soundfile as sf

from concatenative_tts import ConcatenativeTTS
from config import (
    SYLLABLE_AUDIO_DIR,
    SYLLABLES_CSV,
    OUTPUT_CLIPS_DIR,
    OUTPUT_METADATA_CSV,
    OUTPUT_MISSING_CSV,
    TRACE_DIR,
)
from export_utils import export_trace, export_missing_syllables


def generate(texts, write_clips: bool = False, debug: bool = False):
    """
    Synthesize each input text into whistled Silbo audio.

    If write_clips is True, the generated audio and a metadata file are
    written to the output directory defined in config. If debug is True,
    a per-sample synthesis trace is exported. The missing-syllable
    statistics are always exported.
    """
    model = ConcatenativeTTS(SYLLABLES_CSV, SYLLABLE_AUDIO_DIR)

    if write_clips:
        os.makedirs(OUTPUT_CLIPS_DIR, exist_ok=True)
    if debug:
        os.makedirs(TRACE_DIR, exist_ok=True)

    metadata_rows = []

    for i, text in enumerate(texts, start=1):
        if not text:
            continue

        try:
            output, sr, error, trace = model.generate(text)
        except IndexError:
            print(f"Index error while synthesizing: {text}")
            continue

        if error:
            print(f"Skipping (unresolved syllables): {text}")
            continue

        if debug:
            trace_path = os.path.join(TRACE_DIR, f"trace_{i:02d}.csv")
            export_trace(trace, trace_path)

        if write_clips:
            filename = f"Sample {i:02d}.wav"
            filepath = os.path.join(OUTPUT_CLIPS_DIR, filename)
            sf.write(filepath, output, sr)
            metadata_rows.append(f"{filename}|{text}")

    if write_clips:
        with open(OUTPUT_METADATA_CSV, "w", encoding="utf-8") as f:
            for row in metadata_rows:
                f.write(row + "\n")

    missing_syllables = model.get_missing_syllables_stats()
    export_missing_syllables(missing_syllables, OUTPUT_MISSING_CSV)


def read_texts(input_file):
    """Read one text per line from the input file."""
    with open(input_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Synthesize Silbo Gomero audio from input text "
        "using concatenative syllable synthesis."
    )
    parser.add_argument(
        "input_file",
        help="Path to a UTF-8 text file with one utterance per line.",
    )
    parser.add_argument(
        "--write-clips",
        action="store_true",
        help="Write synthesized .wav clips and metadata to the output directory.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Export a per-sample synthesis trace to the trace directory.",
    )
    args = parser.parse_args()

    texts = read_texts(args.input_file)
    generate(texts, write_clips=args.write_clips, debug=args.debug)
