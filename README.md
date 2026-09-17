# Concatenative Synthesis of Silbo Gomero

This repository accompanies a submission on syllable-based concatenative
speech synthesis for **Silbo Gomero**, the whistled register of Spanish
spoken on La Gomera (Canary Islands). It builds a database of syllable
units from existing recordings and concatenates them to synthesize
previously unseen whistled utterances.

## Overview

The pipeline has two stages:

1. **Build the unit database** — clean the recordings, split words into
   syllable units, and enrich them with the metadata used for unit selection.
2. **Generate** — convert input text into whistled audio by selecting and
   concatenating syllable units.

## Data

This project uses the **words** subset of the **Silbo Gomero Speech Corpus**
(OpenSLR SLR137), the only publicly available Silbo corpus, licensed under
**CC BY-NC-SA 4.0**. The corpus is **not** redistributed here and must be
downloaded separately:

1. Download `words.zip` from https://www.openslr.org/137/
2. Extract it and arrange the contents so the layout is:
```
data/
    unprocessed/
        words/
            transc.csv        # transcription table (columns: transcription, path, author)
            clips/            # word recordings
```

## Installation

Requires **Python 3.10+** and the system libraries **ffmpeg** (for `pydub`)
and **libsndfile** (for `soundfile`/`librosa`).

```bash
pip install -r requirements.txt
```

## Usage

**1. Build the unit database** (run once, after placing the corpus):

```bash
python scripts/build_database.py
```

This denoises the recordings, adds phonemic and syllabic transcriptions,
splits each word into syllable units, and computes the unit metadata
(duration, stress, position, speaker, silfateo class). The resulting unit
database is written to `data/syllables/syllables.csv`.

**2. Generate audio from text:**

```bash
python scripts/generate_concatenative.py examples/sample_input.txt --write-clips
```

`sample_input.txt` contains one utterance per line. Synthesized clips are written
to `output/clips/`. Use `--debug` to also export per-utterance selection traces.

## Pipeline components

- `audio_processing.py` — recording cleanup (noise reduction, filtering)
- `build_syllable_columns.py` — phonemic/syllabic transcription of words
- `audio_syllables_splitting.py` — split words into syllable units (split-on-
  silence, per-speaker parameters, validated against expected syllable counts)
- `silfateo.py` — maps Spanish phonemes to the reduced silfateo sound classes
- `postprocess_database.py` — computes unit metadata for selection
- `selection_policy.py` — Viterbi unit selection with a duration/position/
  speaker cost function
- `syllable_resolver.py` — resolves syllables to candidate units, with a
  silfateo-based fallback
- `audio_synthesizer.py` — concatenates the selected units
- `concatenative_tts.py` — orchestrates the synthesis pipeline
- `generate_concatenative.py` — generation entry point
- `build_database.py` — database-build entry point
- `config.py` — data paths and per-speaker parameters
- `text_processor.py` — converts raw text to phonetic syllables (used at generation time)
- `text_processing.py` — DataFrame-level helpers for syllabification and phonetic transcription (used during database build)
- `export_utils.py` — writes per-utterance selection traces and missing-syllable reports to CSV
- `trace_logger.py` — builds structured trace entries during synthesis for debugging

## Citing the data

This project uses the Silbo Gomero Speech Corpus (OpenSLR SLR137). If you use
it, please cite the original work:

```bibtex
@inproceedings{jakubiak23_interspeech,
    author={Agata Jakubiak},
    title={{Whistle-to-text: Automatic recognition of the Silbo Gomero whistled language}},
    year=2023,
    booktitle={Proc. INTERSPEECH 2023},
    pages={3402--3406},
    doi={10.21437/Interspeech.2023-989}
}
```

## Authors
- Radosława Żukowska
- Fernando Ramos López
- Mateo Cámara
- Klara Borowa

## License

Code in this repository is released under the **MIT License** (see `LICENSE`).
The Silbo Gomero Speech Corpus (SLR137) is **not** included and is licensed
separately under CC BY-NC-SA 4.0 by its original author.
