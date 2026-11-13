from datetime import datetime, timezone, timedelta
from shin_mbc.scoring import daily_series
JST = timezone(timedelta(hours=9))

def test_series_shape():
    msgs = [(datetime(2026, 1, 1, 12, 0, tzinfo=JST), "ありがとう、完成した"),
            (datetime(2026, 1, 1, 3, 0, tzinfo=JST), "眠い、寝不足だ")]
    rows = daily_series(msgs)
    assert rows[0]["n"] == 2
    assert rows[0]["night_ratio_pct"] == 50.0
    assert 5 <= rows[0]["condition"] <= 95

def test_empty():
    assert daily_series([]) == []


def test_report_card_has_disclaimer_and_grades():
    from shin_mbc.report import build_report
    msgs = [(datetime(2026, 1, d, 12, 0, tzinfo=JST), "今日は楽しくて嬉しい、完成した") for d in range(1, 15)]
    text = build_report(daily_series(msgs))
    assert "診断ではありません" in text
    assert "成績表" in text and "★" in text
    assert "ひとことで言うと" in text
