# inverter-predictive-ai ⚡

> **AI-powered Predictive Maintenance for Inverter & PCS Manufacturers**
> DC-link Capacitor Aging · IGBT Thermal Trends · Fan Bearing Health · Insulation Monitoring

---

## 🌐 Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://inverter-predictive-ai-hcopvamifmfhgdxawjq4n8.streamlit.app/)

> Try it now — no installation required. See 20 synthetic inverter units, real-time health scores, failure modes, and recommendations.

---

## 🎯 What This Is

A predictive-maintenance concept for solar inverters and Power Conversion Systems (PCS): four weighted health scores (capacitor ageing, IGBT thermal stress, fan bearing health, insulation resistance) combine into a fleet-wide priority view, so a field team can see which units need attention before they fail — not after.

Built for the Indian solar + BESS market context; directly applicable to 50kW–500kW inverter fleets across Rajasthan, Gujarat, Maharashtra, Karnataka, and Tamil Nadu.

This repo is the **Streamlit Cloud deployment** (`streamlit_app.py`) — a single, self-contained app with synthetic fleet data and scoring logic built in, so the live demo above needs no setup. See "How the live demo actually works" below for the exact, honest architecture.

---

## 📸 Screenshots

### Fleet Health Dashboard
![Fleet Dashboard](screenshots/fleet_dashboard.png)

### Alert Priority & Failure Mode Breakdown
![Alert Breakdown](screenshots/alert_breakdown.png)

### Unit Drill-Down — Component Health & Recommendations
![Unit Drilldown](screenshots/unit_drilldown.png)

---

## ⚡ The Business Case

| Metric | Value | Status |
|---|---|---|
| Average unplanned failure cost | ₹2–5 lakh per incident | Industry reference figure, not measured in this repo |
| Detection lead time | 2–4 weeks before failure | Illustrative target for this kind of scoring approach |
| False positive rate, root-cause accuracy | Not yet measured | This deployment hasn't been benchmarked against real failure data — see "Honest framing" below |

---

## 🏗️ How the live demo actually works

```
20 synthetic inverter units (generated with a fixed random seed, 365 days of history)
        ↓
4 weighted health-scoring functions, pure NumPy (no trained ML model in this deployment):
  • Capacitor ageing   — weighted from ESR, capacitance loss, ripple current, temperature
  • IGBT thermal       — weighted from junction temp, switching losses, thermal resistance, Vce
  • Fan health          — weighted from RPM, vibration, current, bearing temperature
  • Insulation          — weighted from IR value, leakage current, polarization index
        ↓
Overall health = 0.7 × weighted average + 0.3 × weakest component
        ↓
Priority bucket: P0 (<30, critical) → P1 (<50) → P2 (<70) → P3 (<85) → P4 (≥85, OK)
        ↓
Remaining-useful-life estimate (simple formula from health score and component lifetime assumption)
        ↓
Streamlit fleet dashboard (overview, alert breakdown, per-unit drill-down)
```

**Honest framing:** the four health scores are hand-weighted formulas, not models trained on labelled failure data — there's no scikit-learn classifier running in this deployment, and the "Cauer thermal network" / FFT vibration analysis described in earlier design notes aren't implemented here either; thermal and vibration health are each a single weighted formula. The fleet is 20 synthetic units generated with a fixed random seed, not real telemetry, so the business-case numbers above are reference/illustrative figures rather than a measured result from this app.

---

## 📦 What's in this repo

```
inverter-predictive-ai/
├── streamlit_app.py              # The entire live app — synthetic fleet generator,
│                                  # the 4 health-scoring functions, and the dashboard UI
├── requirements.txt
├── requirements_hf.txt
├── screenshots/
│   ├── fleet_dashboard.png
│   ├── alert_breakdown.png
│   └── unit_drilldown.png
└── README.md
```

A fuller design (a FastAPI REST endpoint, an n8n alert workflow, trained models per failure mode, a separate ingestion pipeline) exists as an earlier concept, but this public repo is deliberately just the single-file Streamlit Cloud app above — that's what's actually running behind the live demo link.

---

## ⚙️ Tech Stack (this deployment)

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Scoring | Hand-weighted formulas in NumPy (no trained ML model) |
| Data | Synthetic fleet telemetry (20 units, fixed random seed) |
| Dashboard | Streamlit + Pandas |

---

## 🚀 Quick Start (run it yourself)

```bash
git clone https://github.com/PRATdoppelEK/inverter-predictive-ai.git
cd inverter-predictive-ai
pip install -r requirements.txt

streamlit run streamlit_app.py      # → http://localhost:8501
```

No separate data-generation or pipeline step — the synthetic fleet is generated inline in `streamlit_app.py` on load.

---

## 📊 Monitored Signals (what each health score weighs)

### DC-link Capacitor
ESR, capacitance loss, ripple current, temperature — ESR and capacitance loss carry the most weight.

### IGBT Module
Junction temperature, switching losses, thermal resistance, Vce(on) — junction temperature carries the most weight.

### Cooling Fan
RPM drop, vibration, current draw, bearing temperature — RPM and vibration carry the most weight.

### Insulation
Insulation resistance, leakage current, polarization index — IR value carries the most weight.

Each signal maps to a 0–100 sub-score through a weighted formula (see `streamlit_app.py`); the four sub-scores combine into the unit's overall health and P0–P4 priority.

---

## 🔔 Alert Priority System

| Priority | Health score | Meaning | Recommended Response |
|---|---|---|---|
| 🔴 P0 | < 30 | Immediate shutdown risk | Same day — stop unit |
| 🟠 P1 | 30–49 | Service within 48 hours | Dispatch field engineer |
| 🟡 P2 | 50–69 | Schedule within 2 weeks | Plan maintenance |
| 🔵 P3 | 70–84 | Monitor closely | Next service visit |
| ✅ P4 | ≥ 85 | All systems nominal | Continue monitoring |

---

## 🔒 Privacy

- Runs entirely on synthetic, generated-on-load data — nothing confidential
- No external API calls from this deployment

---

## 📅 Build Status

| Component | Status |
|---|---|
| Synthetic fleet generator (20 units) | ✅ Done |
| Capacitor ageing score | ✅ Done |
| IGBT thermal score | ✅ Done |
| Fan health score | ✅ Done |
| Insulation score | ✅ Done |
| Overall health + P0–P4 priority | ✅ Done |
| Remaining-useful-life estimate | ✅ Done |
| Streamlit fleet dashboard | ✅ Done |
| Live Streamlit Cloud deployment | ✅ Done |
| FastAPI REST endpoint, n8n alerting, trained ML models | Design only — not in this deployment |

---

## 👤 Author

**Prateek Gaur** — ML Engineer & Energy Engineering M.Sc. (TU Berlin), Munich
GitHub: [@PRATdoppelEK](https://github.com/PRATdoppelEK)
Email: prateekgaur@gmx.de

---

## 📄 License

MIT
