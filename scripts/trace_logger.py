class TraceLogger:
    """
    Stores synthesis trace.
    """

    def make_entry(
        self,
        syl,
        word,
        pos,
        matches,
        fallback_rule,
        strategy,
        chosen,
        event_type="speech",
    ):
        return {
            "type": event_type,
            "syllable": syl,
            "word": word,
            "position": pos,
            "candidates": matches,
            "fallback": fallback_rule,
            "strategy": strategy,
            "path": chosen,
        }
