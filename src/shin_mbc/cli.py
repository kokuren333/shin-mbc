# -*- coding: utf-8 -*-
"""CLI: shin-mbc analyze file.jsonl [--self-id ID] [--chart out.png] [--nlp sentiment|emotion]"""
from __future__ import annotations
import argparse, json, sys, pathlib
from .loaders import load_jsonl
from .scoring import daily_series
from . import DISCLAIMER_BANNER

def main(argv=None):
    ap = argparse.ArgumentParser(prog="shin-mbc")
    sub = ap.add_subparsers(dest="cmd", required=True)
    an = sub.add_parser("analyze")
    an.add_argument("files", nargs="+")
    an.add_argument("--self-id", default=None)
    an.add_argument("--chart", default=None)
    an.add_argument("--nlp", choices=["sentiment", "emotion"], default=None)
    an.add_argument("--report", default=None, help="also write the plain-language report card to this path")
    rp = sub.add_parser("report", help="print the plain-language report card (NOT a diagnosis)")
    rp.add_argument("files", nargs="+")
    rp.add_argument("--self-id", default=None)
    rp.add_argument("--out", default=None, help="write to file instead of stdout")
    args = ap.parse_args(argv)
    print(DISCLAIMER_BANNER, file=sys.stderr)
    msgs = []
    for f in args.files: msgs.extend(load_jsonl(f, self_id=args.self_id))
    msgs.sort(key=lambda x: x[0])
    rows = daily_series(msgs)
    if args.cmd == "report":
        from .report import build_report
        text = build_report(rows)
        if args.out:
            pathlib.Path(args.out).write_text(text, encoding="utf-8")
            print(f"report written: {args.out}", file=sys.stderr)
        else:
            print(text)
        return 0
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    if args.nlp:
        from .nlp import daily_nlp
        print(json.dumps(daily_nlp(msgs, backend=args.nlp), ensure_ascii=False, indent=2), file=sys.stderr)
    if args.chart:
        from .chart import plot_condition
        plot_condition(rows, args.chart)
        print(f"chart written: {args.chart}", file=sys.stderr)
    if getattr(args, "report", None):
        from .report import build_report
        pathlib.Path(args.report).write_text(build_report(rows), encoding="utf-8")
        print(f"report written: {args.report}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
