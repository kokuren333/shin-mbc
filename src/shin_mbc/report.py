# -*- coding: utf-8 -*-
"""Plain-language state report (状態内申書 / "report card").

Turns the daily heuristic series into a short text report written in
everyday words: a type label, a 5-step grade table, what looked good,
what looked concerning, and the best / hardest days. The language is
deliberately simple (MBTI-style readability), because a chart alone is
hard to read for most people.

THIS IS NOT A DIAGNOSIS. It is a mechanical re-wording of the same
unvalidated heuristic numbers used for the chart. See DISCLAIMER.md.
"""
from __future__ import annotations
import statistics
from . import DISCLAIMER_BANNER

NOT_DIAGNOSIS = ("これは診断ではありません。病名も、治療や受診の必要性も、"
                 "一切判定していません。自分の発言の傾向を言葉で眺めるための、"
                 "機械的な言い換えです。")


def _stars(v):
    return "★" * v + "☆" * (5 - v)


def _grade_rhythm(night_mean):
    if night_mean <= 5: return 5
    if night_mean <= 12: return 4
    if night_mean <= 20: return 3
    if night_mean <= 30: return 2
    return 1


def _grade_energy(mean_condition):
    if mean_condition >= 75: return 5
    if mean_condition >= 70: return 4
    if mean_condition >= 60: return 3
    if mean_condition >= 50: return 2
    return 1


def _grade_stability(sd):
    if sd <= 4: return 5
    if sd <= 6: return 4
    if sd <= 9: return 3
    if sd <= 13: return 2
    return 1


def _grade_positive(balance):
    if balance >= 3: return 5
    if balance >= 1.5: return 4
    if balance >= 0: return 3
    if balance >= -1.5: return 2
    return 1


def _grade_fatigue(fatigue_mean):
    if fatigue_mean <= 0.5: return 5
    if fatigue_mean <= 1.5: return 4
    if fatigue_mean <= 3: return 3
    if fatigue_mean <= 5: return 2
    return 1


def _type_label(mean_c, sd_c, night_mean, trend):
    if night_mean >= 30:
        return ("筋金入りの夜ふくろう型",
                "エンジンがかかるのは夜。深夜の発信が多く、生活リズムは夜側に大きく寄っています。")
    if trend >= 5:
        return ("上り調子・回復型",
                "期間の後半にかけて数字がはっきり上向いています。前半の沈みから持ち直した形です。")
    if trend <= -5:
        return ("お疲れ・下降気味型",
                "期間の後半にかけて数字が下がり気味です。無理が積み重なっている可能性があります。")
    if mean_c >= 72 and sd_c <= 6:
        return ("安定・好調型", "全体に高めで安定しています。大きな崩れのない期間でした。")
    if sd_c >= 10:
        return ("波あり・ジェットコースター型",
                "良い日と沈む日の差が大きいタイプです。波そのものが特徴になっています。")
    if mean_c < 55:
        return ("低空飛行・省エネ型", "全体に低めで推移しています。エネルギーを温存しているような期間です。")
    label = "標準・バランス型"
    desc = "突出した崩れもなく、平均的な範囲で推移しています。"
    if night_mean >= 20:
        label += "（夜型寄り）"
        desc += " ただし深夜の発信はやや多めです。"
    return label, desc


def build_report(rows):
    """rows: output of scoring.daily_series. Returns a markdown string."""
    if not rows:
        return DISCLAIMER_BANNER + "\n\nデータがありませんでした。\n" + NOT_DIAGNOSIS
    conds = [r["condition"] for r in rows]
    mean_c = statistics.mean(conds)
    sd_c = statistics.pstdev(conds) if len(conds) > 1 else 0.0
    night_mean = statistics.mean(r["night_ratio_pct"] for r in rows)
    total_n = sum(r["n"] for r in rows)
    head = rows[:max(1, len(rows) // 2)]
    tail = rows[len(rows) // 2:] or rows[-1:]
    trend = statistics.mean(r["condition"] for r in tail) - statistics.mean(r["condition"] for r in head)
    first7 = statistics.mean(conds[:7])
    last7 = statistics.mean(conds[-7:])
    trend7 = last7 - first7
    best = max(rows, key=lambda r: r["condition"])
    worst = min(rows, key=lambda r: r["condition"])
    pos_bal = statistics.mean(r["positive"] - (r["depress"] + r["anxiety"]) for r in rows)
    fat_mean = statistics.mean(r["fatigue"] for r in rows)
    label, desc = _type_label(mean_c, sd_c, night_mean, trend7)

    grades = [
        ("生活リズム（夜更かしの少なさ）", _grade_rhythm(night_mean),
         f"深夜0〜5時の発信は平均 {night_mean:.0f}% でした"),
        ("元気度（期間全体の調子）", _grade_energy(mean_c),
         f"調子スコアの平均は {mean_c:.0f} / 100 でした"),
        ("安定度（波の小ささ）", _grade_stability(sd_c),
         f"日ごとのブレは {'小さめ' if sd_c <= 6 else '中くらい' if sd_c <= 9 else '大きめ'} でした"),
        ("前向き度（言葉の明るさ）", _grade_positive(pos_bal),
         "ポジティブな言葉と沈みがちな言葉のバランスから"),
        ("元気の残量（疲れサインの少なさ）", _grade_fatigue(fat_mean),
         f"疲れ・眠気の言葉は100投稿あたり平均 {fat_mean:.1f} 回でした"),
    ]

    good, care = [], []
    if night_mean <= 10: good.append("深夜の発信が少なく、生活リズムが保たれています")
    if night_mean >= 25: care.append(f"深夜0〜5時の発信が平均 {night_mean:.0f}% と多めです。睡眠リズムが心配な水準です")
    elif night_mean >= 18: care.append("深夜の発信がやや多めです")
    if statistics.mean(r["positive"] for r in rows) >= 2: good.append("前向きな言葉が比較的多く出ています")
    if trend7 >= 3: good.append("終わりに向けて上向きでした（回復傾向）")
    if trend7 <= -3: care.append("終わりに向けて下がり気味でした")
    if min(conds) >= 50: good.append("大きく沈んだ日がありませんでした")
    if worst["condition"] < 50: care.append(f"いちばん沈んでいたのは {worst['date']}（スコア {worst['condition']:.0f}）でした")
    if fat_mean >= 2: care.append("疲れ・眠気をうかがわせる言葉が目立ちます")
    mean_n = total_n / len(rows)
    busy = [r for r in rows if r["n"] >= max(30, mean_n * 2)]
    if busy: care.append(f"発信量が突出した日が {len(busy)} 日ありました（詰め込み気味の日）")
    if not good: good.append("突出した長所は検出されませんでした（平均的な期間）")
    if not care: care.append("突出した心配材料は検出されませんでした")

    if trend7 >= 3: trend_word = "後半にかけて上向きました"
    elif trend7 <= -3: trend_word = "後半にかけて下がり気味でした"
    else: trend_word = "大きな流れの変化はありませんでした"

    lines = []
    lines.append("# 状態内申書（言葉で読むシンMBC）")
    lines.append("")
    lines.append("> ⚠️ " + NOT_DIAGNOSIS)
    lines.append("")
    lines.append(f"対象期間: {rows[0]['date']} 〜 {rows[-1]['date']}（{len(rows)}日・発信 {total_n} 件から集計）")
    lines.append("")
    lines.append("## ひとことで言うと")
    lines.append(f"**{label}**")
    lines.append(desc)
    lines.append("")
    lines.append("## 成績表（5段階）")
    for name, g, why in grades:
        lines.append(f"- {name}: {_stars(g)}（{g}/5）— {why}")
    lines.append("")
    lines.append("## この期間のこと")
    lines.append(f"平均の調子は {mean_c:.0f} 点で、{trend_word}。"
                 f"いちばん良かったのは {best['date']}（{best['condition']:.0f} 点）、"
                 f"いちばん沈んでいたのは {worst['date']}（{worst['condition']:.0f} 点）でした。")
    lines.append("")
    lines.append("## 良いところ")
    for g in good: lines.append(f"- {g}")
    lines.append("")
    lines.append("## 気になるところ")
    for c in care: lines.append(f"- {c}")
    lines.append("")
    lines.append("---")
    lines.append("※ " + NOT_DIAGNOSIS)
    lines.append("※ スコアは検証されていないヒューリスティクス（単語の出現率・深夜発信の割合・発信量）からの機械的な目安です。気になる状態が続く場合は、こうした道具ではなく医療機関に相談してください。")
    return "\n".join(lines) + "\n"
