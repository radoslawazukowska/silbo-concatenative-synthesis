import random


class SelectionPolicy:
    """
    Implements heuristics for selecting audio candidates.
    """

    def __init__(self, scorer=None):
        self.scorer = scorer or ScoringSelection()

    def viterbi_select(self, syllables, syllable_map):
        candidates = []
        stresses = []

        # build candidate list per syllable
        for syl in syllables:
            entry = syllable_map[syl]
            matches = entry["matches"]
            if not matches:
                return []  # handle outside

            candidates.append(matches)
            stresses.append(1 if "ˈ" in syl else 0)

        T = len(candidates)

        dp = [{} for _ in range(T)]

        # step 0
        for i, c in enumerate(candidates[0]):
            cost = self.scorer.score_candidate(
                syllables[0], stresses[0], c, pos=0, prev=None
            )
            dp[0][i] = (cost, None)

        # forward
        for t in range(1, T):
            for j, curr in enumerate(candidates[t]):
                best_cost = float("inf")
                best_prev = None

                for i, (prev_cost, _) in dp[t - 1].items():
                    prev_c = candidates[t - 1][i]

                    cost = prev_cost
                    cost += self.scorer.score_candidate(
                        syllables[t], stresses[t], curr, pos=t, prev=prev_c
                    )

                    if cost < best_cost:
                        best_cost = cost
                        best_prev = i

                dp[t][j] = (best_cost, best_prev)

        # backtrack
        last = min(dp[T - 1], key=lambda k: dp[T - 1][k][0])

        path = []
        for t in reversed(range(T)):
            path.append(last)
            last = dp[t][last][1]

        path.reverse()

        return [
            {
                "syl": syllables[t],
                "selected": candidates[t][path[t]],
                "matches": candidates[t],
            }
            for t in range(T)
        ]


class ScoringSelection:
    def score_candidate(self, syl, stress, candidate, pos, prev=None):
        score = 0.0

        duration = candidate["duration"]
        z = candidate["duration_z"]
        speaker = candidate["speaker_id"]

        if stress == 1:
            score += abs(z - 0.5)
        else:
            score += abs(z - (-0.5))

        if pos == 0:
            if candidate["position"] == 0:
                score -= 1.0
            else:
                score += 0.5

        if prev is not None:
            score += abs(prev["duration"] - duration) * 0.5

        if prev is not None:
            if prev["speaker_id"] != speaker:
                score += 1.0

        return score
