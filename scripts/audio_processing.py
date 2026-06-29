from pedalboard.io import AudioFile
from pedalboard import (
    Pedalboard,
    NoiseGate,
    Gain,
    Limiter,
    HighpassFilter,
    LowpassFilter,
)
import noisereduce as nr
import numpy as np
import os

from config import UNPROCESSED_WORDS_CLIPS, PROCESSED_WORDS_CLIPS


def normalize(audio):
    peak = np.max(np.abs(audio))
    if peak > 0:
        return audio / peak * 0.95
    return audio


def clean_file(input_path, output_path):
    sr = 22050
    with AudioFile(input_path).resampled_to(sr) as f:
        audio = f.read(f.frames)
    cleaned = clean_whistled_audio(audio, sr)
    with AudioFile(output_path, "w", sr, cleaned.shape[0]) as f:
        f.write(cleaned)


def clean_whistled_audio(audio: AudioFile, sr):
    reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.3)
    board = Pedalboard(
        [
            NoiseGate(threshold_db=-40, ratio=1.2, release_ms=200),
            HighpassFilter(cutoff_frequency_hz=300),
            LowpassFilter(cutoff_frequency_hz=8000),
            Gain(gain_db=6),
            Limiter(threshold_db=-1.0),
        ]
    )
    processed = board(reduced_noise, sr)
    processed = normalize(processed)
    return processed


def clean_all_audio_from_dir(in_dir, out_dir):
    for filename in os.listdir(in_dir):
        in_filepath = os.path.join(in_dir, filename)
        out_filepath = os.path.join(out_dir, filename)
        if os.path.isfile(in_filepath):
            clean_file(in_filepath, out_filepath)


def clean_audio():
    clean_all_audio_from_dir(UNPROCESSED_WORDS_CLIPS, PROCESSED_WORDS_CLIPS)


if __name__ == "__main__":
    clean_audio()
