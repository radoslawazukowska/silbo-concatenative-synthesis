import numpy as np
import librosa
import os


class AudioSynthesizer:
    """
    Loads and concatenates audio segments at a common sample rate
    (taken from the first loaded recording).
    """

    def __init__(self, root_path):
        self.root_path = root_path

    def concatenate(self, paths, silence_len, silence_mark="<SILENCE>"):
        audios = []
        sr_common = None

        for path in paths:
            if path == silence_mark:
                if sr_common is not None:
                    audios.append(np.zeros(int(sr_common * silence_len)))
                continue

            if sr_common is None:
                # First recording sets the common sample rate (native rate).
                record, sr_common = librosa.load(
                    os.path.join(self.root_path, path), sr=None
                )
            else:
                # Resample every subsequent recording to the common rate.
                record, _ = librosa.load(
                    os.path.join(self.root_path, path), sr=sr_common
                )

            audios.append(record)

        if not audios:
            default_sr = 22050
            return np.zeros(int(default_sr * 0.5)), default_sr

        return np.concatenate(audios), sr_common
