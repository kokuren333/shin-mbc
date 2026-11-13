# -*- coding: utf-8 -*-
"""Minimal MCP server (stdio, newline-delimited JSON-RPC, no external deps).

Connect from an MCP client (Muse, Claude Code, etc.) running on the
SAME machine as your data files. All processing is local.

Tools:
  - mbc_explain   : method summary + the full disclaimer
  - mbc_analyze   : daily heuristic condition series from JSONL exports
  - mbc_chart     : render the temperature-style chart PNG

Every tool description and every result carries the non-medical
disclaimer. This server makes NO network calls.
"""
from __future__ import annotations
import json, sys
from . import DISCLAIMER_BANNER

TOOLS = [
    {"name": "mbc_explain",
     "description": "Explain the Shin-MBC heuristic method and its limits. NOT a medical tool; read this first.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "mbc_analyze",
     "description": "Compute daily heuristic condition scores (0-100, unvalidated, NOT a diagnosis) from the user's own JSONL post exports stored locally. Args: files (list of paths), self_id (optional).",
     "inputSchema": {"type": "object", "properties": {
         "files": {"type": "array", "items": {"type": "string"}},
         "self_id": {"type": "string"}}, "required": ["files"]}},
    {"name": "mbc_report",
     "description": "Plain-language report card (state audit in everyday words: type label, 5-step grades, good points, concerns). NOT a diagnosis. Args: files, self_id (optional).",
     "inputSchema": {"type": "object", "properties": {
         "files": {"type": "array", "items": {"type": "string"}},
         "self_id": {"type": "string"}}, "required": ["files"]}},
    {"name": "mbc_chart",
     "description": "Render a temperature-chart style PNG of the heuristic condition series. Args: files, out_png, self_id (optional).",
     "inputSchema": {"type": "object", "properties": {
         "files": {"type": "array", "items": {"type": "string"}},
         "out_png": {"type": "string"},
         "self_id": {"type": "string"}}, "required": ["files", "out_png"]}},
]

def _call(name, args):
    if name == "mbc_explain":
        from .scoring import condition_score  # noqa
        return (DISCLAIMER_BANNER + "\n\nMethod: per-day rates of heuristic Japanese word lists "
                "(depress/anxiety/irritability/fatigue vs positive/productive/activation), "
                "the share of posts between 00:00-05:00, and posting volume are combined into "
                "a 0-100 'condition' index with a 7-day average. Optional NLP backends "
                "(Japanese BERT sentiment / WRIME emotion) can supplement the lexicon rates. "
                "Everything is a relative self-observation signal against one's own baseline. "
                "It is not Measurement-Based Care in the clinical sense, not a validated scale "
                "(it is not PHQ-9/GAD-7/etc.), and not a diagnosis.")
    if name == "mbc_report":
        from .loaders import load_jsonl
        from .scoring import daily_series
        from .report import build_report
        msgs = []
        for f in args["files"]: msgs.extend(load_jsonl(f, self_id=args.get("self_id")))
        msgs.sort(key=lambda x: x[0])
        return build_report(daily_series(msgs))
    if name in ("mbc_analyze", "mbc_chart"):
        from .loaders import load_jsonl
        from .scoring import daily_series
        msgs = []
        for f in args["files"]: msgs.extend(load_jsonl(f, self_id=args.get("self_id")))
        msgs.sort(key=lambda x: x[0])
        rows = daily_series(msgs)
        if name == "mbc_analyze":
            return DISCLAIMER_BANNER + "\n" + json.dumps(rows, ensure_ascii=False)
        from .chart import plot_condition
        plot_condition(rows, args["out_png"])
        return DISCLAIMER_BANNER + f"\nchart written: {args['out_png']}"
    raise ValueError(f"unknown tool {name}")

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try: req = json.loads(line)
        except Exception: continue
        method, rid = req.get("method"), req.get("id")
        if method == "initialize":
            res = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                   "serverInfo": {"name": "shin-mbc", "version": "0.1.0"}}
        elif method == "tools/list":
            res = {"tools": TOOLS}
        elif method == "tools/call":
            p = req.get("params", {})
            try:
                text = _call(p.get("name"), p.get("arguments") or {})
                res = {"content": [{"type": "text", "text": text}], "isError": False}
            except Exception as e:
                res = {"content": [{"type": "text", "text": f"error: {e}"}], "isError": True}
        elif method == "ping":
            res = {}
        elif rid is None:
            continue
        else:
            out = {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"method not found: {method}"}}
            print(json.dumps(out), flush=True); continue
        print(json.dumps({"jsonrpc": "2.0", "id": rid, "result": res}), flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
