import pandas as pd
from silfateo import str_to_silfateo
from enum import Enum


class FallbackRule(Enum):
    RULE_0 = "no fallback"
    RULE_1 = "silfateo"


class SyllableResolver:
    """
    Resolves syllables into candidate audio units using metadata + fallback rules.
    """

    def __init__(self, metadata: pd.DataFrame):
        self.metadata = metadata

    def resolve(self, syl):
        base = syl.replace("ˈ", "")
        stress = 1 if "ˈ" in syl else 0

        fallback_rule = FallbackRule.RULE_0

        match = self.metadata.loc[
            (self.metadata["syllable"] == base) & (self.metadata["stress"] == stress)
        ]

        if len(match) == 0:
            syl_local = str_to_silfateo(base)
            match = self.metadata.loc[(self.metadata["silfateo"] == syl_local)]
            fallback_rule = FallbackRule.RULE_1

        return match, fallback_rule

    def build_cache(self, syllables_by_word):
        syl_map = {}

        for word in syllables_by_word:
            for syl in word:
                if syl in syl_map:
                    continue

                match, rule = self.resolve(syl)

                syl_map[syl] = {"matches": match.to_dict("records"), "fallback": rule}

        return syl_map
