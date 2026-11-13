# -*- coding: utf-8 -*-
"""Heuristic condition scoring.

condition = 68
  + 1.1*positive + 0.7*productive + 0.9*activation      (per 100 posts)
  - 2.2*depress - 2.0*anxiety - 1.4*irritability - 1.3*fatigue
  - 0.55 * max(0, night_ratio_pct - 15)
  - volume overload term
clipped to [5, 95]. 0-100 display scale; bands: >=70 good-ish,
40-70 usual range, <40 low-ish *relative to this formula only*.
This score has NO clinical validity. See DISCLAIMER.md.
"""
from __future__ import annotations
import datetime, collections
from .lexicon import DICTS

def rate_per100(texts, words):
    if not texts: return 0.0
    return 100.0 * sum(t.count(w) for t in texts for w in words) / len(texts)

def condition_score(day_texts, night_ratio_pct, overload_n=0):
    r = {k: rate_per100(day_texts, ws) for k, ws in DICTS.items()}
    cond = (68 + 1.1*r["positive"] + 0.7*r["productive"] + 0.9*r["activation"]
            - 2.2*r["depress"] - 2.0*r["anxiety"] - 1.4*r["irritability"] - 1.3*r["fatigue"]
            - 0.55*max(0.0, night_ratio_pct-15.0) - 0.10*max(0, overload_n))
    return max(5.0, min(95.0, cond)), r

def daily_series(messages, night_sources=None):
    """messages: list of (datetime, text). Returns list of per-day dicts."""
    by = collections.defaultdict(list)
    for dt, t in messages: by[dt.date()].append((dt, t))
    beh = night_sources if night_sources is not None else messages
    by_beh = collections.defaultdict(list)
    for dt, t in beh: by_beh[dt.date()].append(dt)
    rows = []
    for day in sorted(by):
        texts = [t for _, t in by[day]]
        ds = by_beh.get(day, [])
        night = 100.0*sum(1 for dt in ds if dt.hour < 5)/max(len(ds), 1)
        cond, rates = condition_score(texts, night)
        rows.append({"date": day.isoformat(), "n": len(texts), "night_ratio_pct": round(night, 1),
                     "condition": round(cond, 1), **{k: round(v, 2) for k, v in rates.items()}})
    for i, r in enumerate(rows):
        seg = [x["condition"] for x in rows[max(0, i-6):i+1]]
        r["condition_7d"] = round(sum(seg)/len(seg), 1)
    return rows
