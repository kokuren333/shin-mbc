# -*- coding: utf-8 -*-
"""Generic JSONL loaders. Everything runs locally on files the user
themselves exported or collected. No network access anywhere here.

Accepted record shapes (one JSON object per line):
  {"datetime": "<ISO8601>", "text": "..."}
  {"ts": "<ISO8601>", "text": "..."}
  {"created_time": <epoch milliseconds>, "text": "...", "from": "<optional sender id>"}
Pass self_id to keep only one's own messages in chat exports.
"""
from __future__ import annotations
import json, datetime
from datetime import timezone, timedelta
JST = timezone(timedelta(hours=9))

def load_jsonl(path, self_id=None, tz=JST):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            d = json.loads(line)
            if self_id is not None and d.get("from") not in (None, self_id): continue
            text = d.get("text") or ""
            if not text: continue
            if d.get("datetime") or d.get("ts"):
                raw = d.get("datetime") or d.get("ts")
                dt = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(tz)
            elif d.get("created_time"):
                dt = datetime.datetime.fromtimestamp(d["created_time"]/1000, tz=timezone.utc).astimezone(tz)
            else:
                continue
            out.append((dt, text))
    return out
