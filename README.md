# ⚠️⚠️⚠️ 医療ではありません / NOT A MEDICAL TOOL ⚠️⚠️⚠️

> # **最初に必ず [DISCLAIMER.md](DISCLAIMER.md) を読んでください。**
>
> **Shin-MBC は厳密な医学的手法ではありません。診断ツールでも、検証された
> 心理尺度でも、医療機器でもありません。** スコアは単語の出現率と投稿時刻
> などから機械的に作る**ヒューリスティックな目安**で、臨床的妥当性は
> 一切ありません。この数値を根拠に医学的判断をしないでください。
> 利用と解釈は、**すべて各利用者自身の判断と責任**に委ねられます。
>
> Shin-MBC is **not** a rigorous medical method, not a diagnostic tool,
> not a validated scale, and not a medical device. Scores are unvalidated
> heuristics for casual self-observation only. Use and interpretation are
> entirely at each user's own judgment and responsibility.

---

# Shin-MBC

自分の SNS 発言エクスポート（JSONL）をローカルで集計し、「体温表」のように
日々のコンディションの**目安**を時系列で眺めるための、個人向けの
セルフ・オブザベーション支援ツールです。

- 調子スコア（0–100、この計算式の中だけの相対指標）と 7 日平均
- 領域別の語の出現率（抑うつ／不安／易怒／疲労 vs ポジティブ／生産／活性化）
- 深夜（0–5 時）発言割合など、生活リズムの代理指標
- matplotlib による体温表風チャート
- **状態内申書**：グラフが読めない人向けに、タイプ名・5段階の成績表・良いところ／気になるところを言葉だけで伝えるレポート（`shin-mbc report` / MCP `mbc_report`）。もちろんこれも診断ではありません
- オプション：日本語 BERT による感情極性（sentiment）と WRIME 感情（emotion）の補助信号
- MCP サーバー同梱：Muse などの MCP クライアントからローカルで接続可能

**データは外部送信されません。** すべて利用者本人の端末上で処理されます。
他人の発言を分析対象にすることは想定していません。必ず**自分自身の**
エクスポートだけを入力してください。

## 使い方

```bash
pip install .
shin-mbc analyze your_posts.jsonl --chart chart.png
```

入力形式（1 行 1 JSON）：

```json
{"datetime": "2026-01-01T10:00:00+09:00", "text": "投稿本文"}
{"ts": "2026-01-01T10:00:00+09:00", "text": "投稿本文"}
{"created_time": 1767225600000, "text": "投稿本文", "from": "自分のID"}
```

チャット形式のエクスポートで自分の発言だけに絞る場合は `--self-id <自分のID>`。

## NLP オプション（BERT 等）

```bash
pip install ".[nlp]"
shin-mbc analyze your_posts.jsonl --nlp sentiment   # 3値感情極性 (koheiduck/bert-japanese-finetuned-sentiment)
shin-mbc analyze your_posts.jsonl --nlp emotion     # WRIME 8感情 writer側 (patrickramos/bert-base-japanese-v2-wrime-fine-tune)
```

これらのモデルは精神状態の評価用に訓練・検証されたものでは**ありません**。
辞書法と同様、ノイズを含む参考信号としてだけ扱ってください。
モデル本体は初回実行時に Hugging Face からダウンロードされますが、
入力テキストが外部に送信されることはありません。

## MCP として接続する

```bash
pip install .
```

MCP クライアントの設定に以下を追加（`examples/mcp_config.json` 参照）：

```json
{ "mcpServers": { "shin-mbc": { "command": "shin-mbc-mcp", "args": [] } } }
```

公開ツール：`mbc_explain`（手法と限界の説明）／`mbc_analyze`（日次系列）／
`mbc_chart`（チャート生成）、`mbc_report`（言葉版の状態内申書）。すべての応答には非医療ディスクレーマが含まれます。

## 限界（要約）

- 語のヒットには引用・歌詞・創作・他者を論じる文脈が混ざります
- 発言量や深夜率は、仕事・締切・イベントなどでも大きく変動します
- スコアの絶対値に意味はありません。自分のベースラインからの相対変化を
  眺めるためのものです。それでもなお、解釈は各々の判断で行ってください

## License

Apache-2.0
