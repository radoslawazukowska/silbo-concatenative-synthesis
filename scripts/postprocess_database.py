import librosa
import pandas as pd

from config import SYLLABLE_AUDIO_DIR, SYLLABLES_CSV


def parse_stress(syl: str):
    x = str(syl).strip()
    if x.startswith("ˈ"):
        return x[1:], 1
    return x, 0


def extract_position(path):
    if "chunk" in path:
        return int(path.split("chunk")[1].split(".")[0])
    return None


def safe_z(x):
    if len(x) < 2:
        return pd.Series([0.0] * len(x), index=x.index)
    std = x.std()
    if std == 0 or pd.isna(std):
        return pd.Series([0.0] * len(x), index=x.index)
    return (x - x.mean()) / std


def enrich_database():
    df = pd.read_csv(SYLLABLES_CSV, keep_default_na=False)
    # Measure the duration of each syllable unit (in seconds).
    df["duration"] = df["path"].apply(
        lambda p: librosa.get_duration(path=SYLLABLE_AUDIO_DIR + p)
    )

    # Split the phonemic syllable into its base form and a stress flag.
    df[["syllable", "stress"]] = df["fonemas_syllable"].apply(
        lambda x: pd.Series(parse_stress(x))
    )

    # Duration z-score within each (syllable, stress) group.
    df["duration_z"] = df.groupby(["syllable", "stress"])["duration"].transform(safe_z)

    # Position of the unit within its source word (from the chunk index).
    df["position"] = df["path"].apply(extract_position)

    # Integer speaker id derived from the author name.
    df["speaker_id"] = df["author"].astype("category").cat.codes
    df.to_csv(SYLLABLES_CSV, index=False)


if __name__ == "__main__":
    enrich_database()
