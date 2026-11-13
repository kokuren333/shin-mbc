---
name: shin-mbc
description: Heuristic self-observation ("Shin-MBC") from the user's OWN SNS text exports — daily condition-style chart. NOT a medical tool.
---

# Shin-MBC (agent skill)

When the user asks to visualise their own posting history as a
condition/temperature chart:

1. **Read DISCLAIMER.md first** and repeat its core points to the user:
   not medical, not a diagnosis, not a validated scale, interpretation
   is the user's own judgment.
2. Use ONLY the user's own exported posts, processed locally.
   Never upload raw posts anywhere. Report aggregates only.
3. Run: `shin-mbc analyze <files...> [--self-id ID] --chart out.png`
   or call the MCP tools `mbc_analyze` / `mbc_chart`.
4. Present the 7-day average as the trend; flag data gaps (missing
   days/sources) explicitly; note partial days as partial.
5. Never phrase a score as a health assessment, never suggest medical
   action based on it. If the user expresses acute distress, respond
   supportively and point to professional/public support resources —
   the chart is irrelevant in that moment.
