# news-image-20261117

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/Ngntier/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/Ngntier/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

A newspaper front page drawn entirely in code that sums up the world news of
**Tuesday 17 November 2026** in one 1024×1024 image: Ukraine's strike on the
Kerch Bridge, Trump landing in Manila for ASEAN, tankers burning in the Strait
of Hormuz, ULA's Vulcan failure — plus a ticker of the day's other stories
(JPMorgan outage, Nvidia earnings, UK sanctions, Japan scrambling jets).

Every headline, name and number in the image comes from a real report read on
17–18 November 2026; the sources are listed in [NEWS.md](NEWS.md). Claims
that could not be independently verified (the Hormuz mine strikes) are
captioned as reported, not as confirmed fact. All art is drawn with a
hand-rolled rasterizer and an embedded bitmap font in pure Python standard
library — no photos, no copied artwork, no network at runtime, no
third-party packages.

## Run it

```sh
python3 main.py
```

Writes `entry.png` to `$MAKEFUN_OUTPUT_DIR`, or `/output` when it exists,
otherwise `./entry.png`. The output is deterministic: two runs produce
byte-identical PNGs (26 KB or less, 1024×1024, within the 1 MiB cap).

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
