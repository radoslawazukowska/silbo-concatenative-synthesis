from pydub import AudioSegment
from pydub.silence import split_on_silence
import pandas as pd
import ast
import os

from config import (
    SPEAKER_PARAMS,
    TRANSC_CSV,
    PROCESSED_WORDS_DIR,
    SYLLABLE_AUDIO_DIR,
    DESC_CSV,
    SYLLABLES_CSV,
)


class SplitAudio:
    @staticmethod
    def split(input, output, min_silence_len=500, silence_thresh=-16):
        file = AudioSegment.from_wav(input)
        audio_chunks = SplitAudio.split_audio(file, min_silence_len, silence_thresh)
        for i, chunk in enumerate(audio_chunks):
            out_file = f"{output}-chunk{i}.wav"
            chunk.export(out_file, format="wav")

    @staticmethod
    def split_audio(audio: AudioSegment, min_silence_len, silence_thresh):
        audio_chunks = split_on_silence(
            audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh
        )
        return audio_chunks

    @staticmethod
    def split_in_chunks(
        input: str, output: str, chunks: int, min_silence_len=50, silence_thresh=-16
    ):
        audio_chunks = SplitAudio.split_file(input, min_silence_len, silence_thresh)
        if len(audio_chunks) == chunks:
            for i, chunk in enumerate(audio_chunks):
                out_file = f"{output}-chunk{i}.wav"
                chunk.export(out_file, format="wav")
        return len(audio_chunks)

    @staticmethod
    def split_file(file: str, min_silence_len=50, silence_thresh=-16):
        audio = AudioSegment.from_wav(file)
        audio_chunks = SplitAudio.split_audio(audio, min_silence_len, silence_thresh)
        return audio_chunks


def find_best_params():
    msl_params = [75, 70, 65, 60]
    st_params = [-16, -12, -10]
    transc_df = pd.read_csv(TRANSC_CSV)
    syl_count_df = transc_df[transc_df["path"].str.contains("04-", na=False)][
        ["path", "syllables"]
    ].copy()
    syl_count_df["audio"] = syl_count_df["path"].apply(
        lambda x: AudioSegment.from_wav(PROCESSED_WORDS_DIR + x)
    )
    syl_count_df["num_syl"] = (
        syl_count_df["syllables"].apply(ast.literal_eval).apply(lambda x: len(x[0]))
    )

    for msl in msl_params:
        for st in st_params:
            print(f"Counting for {msl} ms and {st} dB")
            syl_count_df[f"{msl}_{st}_predict"] = syl_count_df["audio"].apply(
                lambda x: len(SplitAudio.split_audio(x, msl, st))
            )
            syl_count_df[f"{msl}_{st}_diff"] = (
                syl_count_df[f"{msl}_{st}_predict"] - syl_count_df["num_syl"]
            )

    diff_cols = syl_count_df.filter(like="_diff")
    extremes = []
    for col in diff_cols.columns:
        idx_max = diff_cols[col].idxmax()
        idx_min = diff_cols[col].idxmin()
        zero_count = (diff_cols[col] == 0).sum()

        extremes.append(
            {
                "column": col,
                "max_overestimation": diff_cols[col].loc[idx_max],
                "path_max_over": syl_count_df.loc[idx_max, "path"],
                "max_underestimation": diff_cols[col].loc[idx_min],
                "path_max_under": syl_count_df.loc[idx_min, "path"],
                "zero_diff_count": zero_count,
            }
        )
    extremes_df = pd.DataFrame(extremes)
    print(extremes_df)

    syl_count_df = syl_count_df.drop("audio", axis=1)


def process_recordings(recordings_dir_in, recordings_dir_out, input_csv, output_csv):
    desc_df = pd.read_csv(input_csv)

    desc_df["fonemas_pl_syl"] = desc_df["fonemas_pl_syl"].apply(ast.literal_eval)
    desc_df["syllables"] = desc_df["syllables"].apply(ast.literal_eval)

    speaker_params = SPEAKER_PARAMS

    split_results = []
    syllable_rows = []

    desc_df["min_silence_len"] = None
    desc_df["silence_thresh"] = None
    desc_df["produced_chunks"] = None

    for idx in desc_df.index:
        transcription = desc_df.at[idx, "transcription"]
        relative_path = desc_df.at[idx, "path"]
        speaker = os.path.basename(relative_path).split("-")[0]
        expected_chunks = int(desc_df.at[idx, "num_syl"])
        fon_syllables = desc_df.at[idx, "fonemas_pl_syl"]
        lit_syllables = [x for xs in desc_df.at[idx, "syllables"] for x in xs]

        input_path = os.path.join(recordings_dir_in, relative_path)
        output_path = os.path.join(recordings_dir_out, relative_path.split(".")[0])

        speaker_p = speaker_params[speaker]
        produced_chunks = SplitAudio.split_in_chunks(
            input=input_path,
            output=output_path,
            chunks=expected_chunks,
            min_silence_len=speaker_p["min_silence_len"],
            silence_thresh=speaker_p["silence_thresh"],
        )
        desc_df.at[idx, "min_silence_len"] = speaker_p["min_silence_len"]
        desc_df.at[idx, "silence_thresh"] = speaker_p["silence_thresh"]
        desc_df.at[idx, "produced_chunks"] = produced_chunks

        split_results.append(produced_chunks == expected_chunks)
        if produced_chunks == expected_chunks:
            if len(fon_syllables) != len(lit_syllables):
                print(f"{fon_syllables}\t{lit_syllables}")
            for i in range(expected_chunks):
                syllable_rows.append(
                    {
                        "author": speaker,
                        "transcription": transcription,
                        "path": f"{relative_path.split('.')[0]}-chunk{i}.wav",
                        "fonemas_syllable": fon_syllables[i],
                        "lit_syllable": lit_syllables[i],
                    }
                )

    desc_df["split"] = split_results

    not_correct_df = desc_df[desc_df["split"] == False].copy()
    not_correct_df.to_csv(output_csv.split(".")[0] + "_incorrect.csv", index=False)

    cleaned_words_df = desc_df[desc_df["split"] == True].copy()
    cleaned_words_df.drop(columns=["split"], inplace=True)
    cleaned_words_df.to_csv(output_csv, index=False)

    syllables_df = pd.DataFrame(syllable_rows)
    syllables_df.to_csv(SYLLABLES_CSV, index=False)


def create_desc_file(input, output):
    df = pd.read_csv(input)
    df["num_syl"] = df["fonemas_pl_syl"].apply(ast.literal_eval).apply(len)
    df.to_csv(output, index=False)


def build_units():
    create_desc_file(TRANSC_CSV, DESC_CSV)
    process_recordings(
        PROCESSED_WORDS_DIR,
        SYLLABLE_AUDIO_DIR,
        DESC_CSV,
        DESC_CSV,
    )


if __name__ == "__main__":
    build_units()
