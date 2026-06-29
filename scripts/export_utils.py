import pandas as pd
from enum import Enum


def export_trace(trace, path):
    df = pd.DataFrame([
        {
            "syllable": t["syllable"],
            "word": t["word"],
            "position": t["position"],
            "path": t["path"],
            "strategy": t["strategy"],
            "fallback": t["fallback"].value if isinstance(t["fallback"], Enum) else t["fallback"]
        }
        for t in trace if t["type"] == "speech"
    ])
    df.to_csv(path, index=False)


def export_missing_syllables(missing_dict, path):
    df = pd.DataFrame(
        [
            (syl, data["count"], ",".join(data["words"]))
            for syl, data in missing_dict.items()
        ],
        columns=["syllable", "count", "words"]
    )

    df = df.sort_values(by="count", ascending=False)
    df.to_csv(path, index=False)