# -*- coding: utf-8 -*-
"""Optional NLP backends (transformer models). Heuristic assistance only.

Two pluggable backends, both *optional* (install with `pip install .[nlp]`):

1. Sentiment (3-class, Japanese BERT):
   koheiduck/bert-japanese-finetuned-sentiment
   -> per-post P(positive) / P(negative) / P(neutral)
2. Emotion (WRIME fine-tuned Japanese BERT, Plutchik 8 emotions x
   writer/reader): patrickramos/bert-base-japanese-v2-wrime-fine-tune
   -> per-post writer_* emotion intensities (regression, WRIME 0-3 scale).
   writer_sadness / writer_fear / writer_anger loosely correspond to
   the lexicon domains depress / anxiety / irritability.

These models were NOT trained or validated for mental-health
assessment. Their outputs are noisy signals for self-observation
only. Model weights are downloaded from Hugging Face on first use;
the texts themselves are processed locally and are not sent anywhere
else by this code.
"""
from __future__ import annotations

SENTIMENT_MODEL = "koheiduck/bert-japanese-finetuned-sentiment"
EMOTION_MODEL = "patrickramos/bert-base-japanese-v2-wrime-fine-tune"
WRITER_EMOTIONS = ["joy","sadness","anticipation","surprise","anger","fear","disgust","trust"]

def _pipeline(model, **kw):
    try:
        from transformers import pipeline
    except ImportError as e:
        raise RuntimeError("NLP extras not installed: pip install 'shin-mbc[nlp]'") from e
    return pipeline("text-classification", model=model, top_k=None, **kw)

def sentiment_scores(texts, model=SENTIMENT_MODEL, batch_size=32):
    """Returns list of dicts {POSITIVE, NEGATIVE, NEUTRAL} probabilities."""
    clf = _pipeline(model)
    out = []
    for i in range(0, len(texts), batch_size):
        batch = [t[:512] for t in texts[i:i+batch_size]]
        for res in clf(batch):
            d = {r["label"].upper(): float(r["score"]) for r in res}
            out.append({"positive": d.get("POSITIVE", 0.0), "negative": d.get("NEGATIVE", 0.0),
                        "neutral": d.get("NEUTRAL", 0.0)})
    return out

def emotion_scores(texts, model=EMOTION_MODEL, batch_size=32):
    """Returns list of dicts of writer_* emotion intensities in [0,1] (sigmoid)."""
    # This model is a REGRESSION fine-tune: outputs are raw emotion
    # intensities on the WRIME 0-3 scale (may slightly exceed it).
    # top_k=None pipelines return scores that are the raw logits here,
    # which for this checkpoint equal the regressed intensities.
    clf = _pipeline(model)
    out = []
    for i in range(0, len(texts), batch_size):
        batch = [t[:512] for t in texts[i:i+batch_size]]
        for res in clf(batch):
            d = {}
            for r in res:
                lab = r["label"]
                if lab.startswith("writer_"):
                    d[lab[len("writer_"):]] = max(0.0, min(3.0, float(r["score"])))
            out.append(d)
    return out

def daily_nlp(messages, backend="sentiment"):
    """Aggregate an NLP backend to per-day means."""
    import collections
    texts = [t for _, t in messages]
    scores = sentiment_scores(texts) if backend == "sentiment" else emotion_scores(texts)
    by = collections.defaultdict(list)
    for (dt, _), s in zip(messages, scores): by[dt.date()].append(s)
    rows = []
    for day in sorted(by):
        keys = by[day][0].keys()
        rows.append({"date": day.isoformat(), "n": len(by[day]),
                     **{k: round(sum(s.get(k, 0.0) for s in by[day])/len(by[day]), 4) for k in keys}})
    return rows
