# Meta Ads Commander v4 — Genius Edition

A production-grade Streamlit web application for Meta (Facebook) Ads campaign analytics, monitoring, and optimization.

## Features

- **Windows 11 Design Language** — Dark/Light mode with glassmorphism, 150+ CSS design tokens
- **220+ Metrics** across 4 tiers:
  - Tier 1: 26 Standard KPIs (CTR, CPC, ROAS, etc.)
  - Tier 2: 50 AXIOM metrics (advanced efficiency, quality scores)
  - Tier 3: 120 ARCHON metrics (17-group deep analytics)
  - Tier 4: 24 Composite Scores (multi-signal health indicators)
- **52 UI Components** across 8 categories (layout, navigation, data display, charts, filters, actions, feedback, config)
- **12 Chart Types** — Line, Bar, Pie, Area, Scatter, Heatmap, Funnel, Gauge, Sparkline, Trend, Forecast, Anomaly
- **8 Production Engines** — Metric, Analytics, Alert, Export, Scheduler + 3 metric registries
- **5 Page Views** — Dashboard, Analytics, Alerts, Export, Settings
- **25 Alert Rules** across 6 categories with cooldown management
- **6 Export Formats** — CSV, XLSX, JSON, PowerBI (Ad/AdSet/Campaign) with anonymization
- **Advanced Analytics** — Trend analysis (OLS), anomaly detection (z-score/IQR), Holt-Winters forecasting, cohort analysis

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Architecture

```
meta-ads-commander-v4/
├── app.py                    # Main entry point
├── core/                     # State, entities, demo data, pipeline, validation
├── engines/                  # Metric computation, analytics, alerts, export, scheduler
├── ui/
│   ├── styles.py             # Windows 11 CSS themes (dark/light)
│   └── components/           # 52 reusable UI components
├── page_views/               # 5 page compositions (Dashboard, Analytics, Alerts, Export, Settings)
├── integrations/             # Slack & Email notification dispatchers
├── tests/                    # 8 test functions, 39+ assertions
└── config/                   # Scheduler config & export templates
```

## Demo Data

Auto-generates realistic campaign data with seed=42:
- 2 ad accounts, 5 campaigns, 7 ad sets, 12 ads
- 60 days of daily metrics with seasonal patterns and noise
- 37 columns per row including video metrics and quality ranks

## Requirements

- Python 3.10+
- Streamlit >= 1.28.0
- Pandas, NumPy, Plotly, OpenPyXL, SciPy

## License

MIT
