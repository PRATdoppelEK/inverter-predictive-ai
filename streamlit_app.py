"""
Inverter Predictive AI — Hugging Face Spaces
Self-contained app (no external dependencies except numpy/pandas/streamlit)

Demonstrates:
    - DC-link Capacitor aging health scoring
    - IGBT thermal health scoring
    - Fan bearing health scoring
    - Insulation resistance monitoring
    - Fleet health dashboard with synthetic demo data

Author: Prateek Gaur
Project: inverter-predictive-ai
"""

import numpy as np
import pandas as pd
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Inverter Predictive AI",
    page_icon="⚡",
    layout="wide",
)

st.markdown("""
<style>
    .metric-card { background:#f8fafc; border-radius:8px; padding:12px; margin:4px; }
    .alert-p0 { background:#fee2e2; border-left:4px solid #ef4444; padding:10px 14px; border-radius:4px; margin:4px 0; }
    .alert-p1 { background:#ffedd5; border-left:4px solid #f97316; padding:10px 14px; border-radius:4px; margin:4px 0; }
    .alert-p2 { background:#fef9c3; border-left:4px solid #eab308; padding:10px 14px; border-radius:4px; margin:4px 0; }
    .alert-ok  { background:#dcfce7; border-left:4px solid #16a34a; padding:10px 14px; border-radius:4px; margin:4px 0; }
</style>
""", unsafe_allow_html=True)

# ── Health scoring functions ──────────────────────────────────────────────────

def capacitor_health(esr_mohm, cap_uf, ripple_a, temp_c, nominal_cap=1000):
    esr_s   = max(0, 100 - 90 * max(0, esr_mohm - 5) / 15)
    cap_loss= max(0, (nominal_cap - cap_uf) / nominal_cap * 100)
    cap_s   = max(0, 100 - 90 * max(0, cap_loss - 5) / 20)
    rip_s   = max(0, 100 - 90 * max(0, ripple_a - 8) / 10)
    tmp_s   = max(0, 100 - 95 * max(0, temp_c - 45) / 30)
    score   = 0.40*esr_s + 0.30*cap_s + 0.20*rip_s + 0.10*tmp_s
    return round(np.clip(score, 0, 100), 1)

def igbt_health(tj_c, sw_loss_w, rth_jc, vce_v):
    tj_s  = max(0, 100 - 95 * max(0, tj_c - 100) / 50)
    sw_s  = max(0, 100 - 95 * max(0, sw_loss_w - 120) / 160)
    rth_s = max(0, 100 - 95 * max(0, rth_jc - 0.15) / 0.17)
    vce_s = max(0, 100 - 90 * max(0, vce_v - 1.8) / 0.7)
    score = 0.35*tj_s + 0.30*sw_s + 0.25*rth_s + 0.10*vce_s
    return round(np.clip(score, 0, 100), 1)

def fan_health(rpm, vibration, current, bearing_temp, nominal_rpm=2800):
    rpm_s  = max(0, 100 - 95 * max(0, nominal_rpm - rpm) / 600)
    vib_s  = max(0, 100 - 95 * max(0, vibration - 2.0) / 5.1)
    cur_s  = max(0, 100 - 90 * max(0, current - 1.2) / 0.7)
    btmp_s = max(0, 100 - 95 * max(0, bearing_temp - 40) / 40)
    score  = 0.35*rpm_s + 0.35*vib_s + 0.20*cur_s + 0.10*btmp_s
    return round(np.clip(score, 0, 100), 1)

def insulation_health(ir_mohm, leakage_ma, pi):
    ir_s   = max(0, 100 - 95 * max(0, 100 - ir_mohm) / 90)
    leak_s = max(0, 100 - 95 * max(0, leakage_ma - 2) / 28)
    pi_s   = max(0, 100 - 95 * max(0, 4.0 - pi) / 3.0)
    score  = 0.45*ir_s + 0.35*leak_s + 0.20*pi_s
    return round(np.clip(score, 0, 100), 1)

def overall_health(cap_h, igbt_h, fan_h, ins_h):
    weighted = 0.30*cap_h + 0.35*igbt_h + 0.20*fan_h + 0.15*ins_h
    minimum  = min(cap_h, igbt_h, fan_h, ins_h)
    return round(0.7*weighted + 0.3*minimum, 1)

def get_priority(health):
    if health < 30:  return "P0", "🔴 CRITICAL"
    if health < 50:  return "P1", "🟠 HIGH"
    if health < 70:  return "P2", "🟡 WARNING"
    if health < 85:  return "P3", "🔵 MONITOR"
    return "P4", "✅ OK"

def get_rul(health, component="general"):
    lifetimes = {"cap": 365*15, "igbt": 365*20, "fan": 365*5, "ins": 365*10, "general": 365*10}
    base = lifetimes.get(component, 365*10)
    return max(0, int(base * (health/100)**2))

# ── Generate synthetic fleet data ─────────────────────────────────────────────

@st.cache_data
def generate_fleet_demo():
    rng = np.random.default_rng(42)
    units = []
    models_list = ["PCS-50kW", "PCS-100kW", "PCS-250kW", "PCS-500kW"]
    sites = ["Rajasthan", "Gujarat", "Maharashtra", "Karnataka", "Tamil Nadu"]

    for i in range(20):
        deg = rng.uniform(0.0, 0.95)
        cap_h  = capacitor_health(5+20*deg, 1000-250*deg, 8+12*deg, 45+30*deg)
        igbt_h = igbt_health(95+55*deg, 120+160*deg, 0.15+0.17*deg, 1.8+0.7*deg)
        fan_h  = fan_health(2800-600*deg, 1.5+5.5*deg, 1.2+0.7*deg, 35+45*deg)
        ins_h  = insulation_health(100-90*deg, 2+48*deg, 4.0-3.0*deg)
        ov_h   = overall_health(cap_h, igbt_h, fan_h, ins_h)
        pri, label = get_priority(ov_h)

        units.append({
            "unit_id":      f"INV-{i+1:03d}",
            "model":        rng.choice(models_list),
            "site":         rng.choice(sites),
            "health":       ov_h,
            "priority":     pri,
            "label":        label,
            "cap_health":   cap_h,
            "igbt_health":  igbt_h,
            "fan_health":   fan_h,
            "ins_health":   ins_h,
            "rul_days":     get_rul(ov_h),
            "failure_mode": (
                "thermal_fatigue"    if igbt_h == min(cap_h,igbt_h,fan_h,ins_h) else
                "capacitor_aging"    if cap_h  == min(cap_h,igbt_h,fan_h,ins_h) else
                "cooling_degradation"if fan_h  == min(cap_h,igbt_h,fan_h,ins_h) else
                "insulation_failure"
            ) if ov_h < 70 else "healthy",
        })
    return pd.DataFrame(units).sort_values("health")

fleet_df = generate_fleet_demo()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚡ Inverter Predictive AI")
    st.markdown("**Fleet Health Monitoring**")
    st.markdown("*AI-powered predictive maintenance*")
    st.markdown("---")
    st.markdown("### 📊 Fleet Stats")
    st.metric("Total Units",  len(fleet_df))
    st.metric("Avg Health",   f"{fleet_df['health'].mean():.1f}%")
    st.metric("Critical (P0/P1)", int((fleet_df["priority"].isin(["P0","P1"])).sum()))
    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.markdown("[GitHub Repo](https://github.com/PRATdoppelEK/inverter-predictive-ai)")
    st.markdown("[Author: Prateek Gaur](https://github.com/PRATdoppelEK)")
    st.markdown("---")
    page = st.radio("Navigation", ["🏠 Fleet Dashboard", "🔍 Unit Assessment", "📖 About"])

# ── Page: Fleet Dashboard ─────────────────────────────────────────────────────

if page == "🏠 Fleet Dashboard":
    st.markdown("# ⚡ Inverter Fleet Health Dashboard")
    st.markdown("AI-powered predictive maintenance — DC-link Capacitor · IGBT Thermal · Fan Bearing · Insulation")
    st.markdown("---")

    # Overview metrics
    n_crit = int((fleet_df["priority"].isin(["P0","P1"])).sum())
    n_warn = int((fleet_df["priority"] == "P2").sum())
    n_ok   = int((fleet_df["priority"].isin(["P3","P4"])).sum())

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("Total Units",    len(fleet_df))
    with c2: st.metric("Avg Health",     f"{fleet_df['health'].mean():.1f}%")
    with c3: st.metric("🔴 Critical",    n_crit)
    with c4: st.metric("🟡 Warning",     n_warn)
    with c5: st.metric("✅ Healthy",     n_ok)

    # Critical alerts
    critical = fleet_df[fleet_df["priority"].isin(["P0","P1"])]
    if not critical.empty:
        st.markdown("### 🚨 Active Alerts")
        for _, r in critical.iterrows():
            css = "alert-p0" if r["priority"]=="P0" else "alert-p1"
            st.markdown(
                f'<div class="{css}"><strong>{r["unit_id"]}</strong> — '
                f'{r["label"]} | Health: {r["health"]}% | '
                f'Failure: {r["failure_mode"].replace("_"," ").title()} | '
                f'RUL: {r["rul_days"]} days</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Fleet health bar chart
    st.markdown("### 📊 Fleet Health Overview")
    chart_df = fleet_df.set_index("unit_id")[["health"]].copy()
    st.bar_chart(chart_df, color="#2563eb")

    # Full fleet table
    st.markdown("### 🏭 All Units")
    display = fleet_df[[
        "unit_id","model","site","health","label","failure_mode",
        "rul_days","cap_health","igbt_health","fan_health","ins_health"
    ]].rename(columns={
        "unit_id":"Unit","model":"Model","site":"Site",
        "health":"Health%","label":"Status","failure_mode":"Failure Mode",
        "rul_days":"RUL(d)","cap_health":"Cap%",
        "igbt_health":"IGBT%","fan_health":"Fan%","ins_health":"Ins%"
    })
    st.dataframe(display.round(1), hide_index=True, use_container_width=True)

    # Priority distribution
    st.markdown("### 🔀 Priority Distribution")
    p_counts = fleet_df["priority"].value_counts().reindex(
        ["P0","P1","P2","P3","P4"], fill_value=0
    )
    st.bar_chart(p_counts)

# ── Page: Unit Assessment ─────────────────────────────────────────────────────

elif page == "🔍 Unit Assessment":
    st.markdown("# 🔍 Single Unit Health Assessment")
    st.markdown("Enter inverter sensor readings to get an instant health assessment.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚡ DC-link Capacitor")
        esr     = st.slider("ESR (mΩ)",            5.0,  25.0,  8.5,  0.1)
        cap_uf  = st.slider("Capacitance (μF)",   750.0,1000.0,980.0, 5.0)
        ripple  = st.slider("Ripple Current (A)",   5.0,  20.0,  9.5,  0.1)
        cap_temp= st.slider("Capacitor Temp (°C)", 30.0,  80.0, 48.0,  0.5)

        st.markdown("### 💨 Cooling Fan")
        rpm       = st.slider("Fan RPM",          2100.0, 2900.0, 2750.0, 10.0)
        vibration = st.slider("Vibration (mm/s)",    0.5,    9.0,    1.8,  0.1)
        fan_curr  = st.slider("Fan Current (A)",     0.8,    2.0,    1.25, 0.05)
        bear_temp = st.slider("Bearing Temp (°C)",  25.0,   90.0,   42.0,  0.5)

    with col2:
        st.markdown("### 🔥 IGBT Module")
        tj      = st.slider("Junction Temp (°C)",   60.0, 155.0, 105.0,  0.5)
        sw_loss = st.slider("Switching Loss (W)",   80.0, 300.0, 142.0,  1.0)
        rth     = st.slider("Rth_jc (K/W)",         0.13,   0.36,   0.162, 0.001)
        vce     = st.slider("Vce_on (V)",            1.6,    2.6,    1.85,  0.01)

        st.markdown("### 🛡️ Insulation")
        ir_val  = st.slider("IR Value (MΩ)",         5.0,  110.0,  88.0,  1.0)
        leakage = st.slider("Leakage Current (mA)",  1.0,   50.0,   3.5,  0.1)
        pi_val  = st.slider("Polarization Index",    0.5,    4.5,   3.5,  0.1)

    # Calculate scores
    cap_h  = capacitor_health(esr, cap_uf, ripple, cap_temp)
    igbt_h = igbt_health(tj, sw_loss, rth, vce)
    fan_h  = fan_health(rpm, vibration, fan_curr, bear_temp)
    ins_h  = insulation_health(ir_val, leakage, pi_val)
    ov_h   = overall_health(cap_h, igbt_h, fan_h, ins_h)
    pri, label = get_priority(ov_h)

    st.markdown("---")
    st.markdown("### 📊 Assessment Results")

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("Overall Health",  f"{ov_h}%")
    with c2: st.metric("⚡ Capacitor",    f"{cap_h}%")
    with c3: st.metric("🔥 IGBT",         f"{igbt_h}%")
    with c4: st.metric("💨 Fan",          f"{fan_h}%")
    with c5: st.metric("🛡️ Insulation",   f"{ins_h}%")

    css = ("alert-p0" if pri=="P0" else "alert-p1" if pri=="P1"
           else "alert-p2" if pri=="P2" else "alert-ok")
    rul = get_rul(ov_h)
    st.markdown(
        f'<div class="{css}"><strong>{label}</strong> — '
        f'Overall Health: {ov_h}% | Estimated RUL: {rul} days</div>',
        unsafe_allow_html=True
    )

    # Component bar chart
    comp_df = pd.DataFrame({
        "Component": ["Capacitor","IGBT","Fan","Insulation"],
        "Health (%)": [cap_h, igbt_h, fan_h, ins_h],
    }).set_index("Component")
    st.bar_chart(comp_df, color="#2563eb")

    # Recommendations
    st.markdown("### 📋 Recommendations")
    recs = []
    if esr > 12:    recs.append(f"⚠️ ESR = {esr}mΩ — capacitor aging, plan replacement")
    if tj > 125:    recs.append(f"🔥 Tj = {tj}°C — reduce switching frequency or improve heatsink")
    if vibration>4.5: recs.append(f"💨 Vibration = {vibration} mm/s — bearing wear, schedule replacement")
    if ir_val < 50: recs.append(f"🛡️ IR = {ir_val}MΩ — insulation degraded, inspect for moisture")
    if rth > 0.25:  recs.append(f"🔥 Rth_jc = {rth} K/W — thermal paste degraded, inspect mounting")
    if not recs:    recs.append("✅ All parameters within normal range — continue standard monitoring")
    for rec in recs:
        st.markdown(f"• {rec}")

# ── Page: About ───────────────────────────────────────────────────────────────

elif page == "📖 About":
    st.markdown("# ⚡ Inverter Predictive AI")
    st.markdown("---")
    st.markdown("""
## About This Project

**inverter-predictive-ai** is an AI-powered predictive maintenance system for
solar inverters and Battery Energy Storage Systems (BESS) in the Indian market.

### What it monitors

| Component | Failure Mode | Key Signal |
|---|---|---|
| DC-link Capacitor | Aging, dielectric breakdown | ESR drift |
| IGBT Module | Thermal fatigue, bond wire | Junction temperature |
| Cooling Fan | Bearing wear | RPM drop + vibration |
| Insulation | Moisture ingress, ground fault | IR resistance drop |

### Alert Priority System

| Priority | Meaning | Response |
|---|---|---|
| 🔴 P0 | Shutdown risk | Same day |
| 🟠 P1 | Service within 48h | Dispatch engineer |
| 🟡 P2 | Schedule in 2 weeks | Plan maintenance |
| 🔵 P3 | Monitor | Next service visit |
| ✅ P4 | All nominal | Continue monitoring |

### Business Case
- Average unplanned failure cost: ₹2–5 lakh per incident
- Detection lead time: 2–4 weeks before failure
- Applicable to: 50kW–500kW inverter fleets across India

### Author
**Prateek Gaur** — ML Engineer & Energy Engineering M.Sc. (TU Berlin), Munich

[GitHub](https://github.com/PRATdoppelEK) | [inverter-predictive-ai](https://github.com/PRATdoppelEK/inverter-predictive-ai)
""")

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#9ca3af;font-size:12px;'>"
    "inverter-predictive-ai · Built by Prateek Gaur · "
    "<a href='https://github.com/PRATdoppelEK'>github.com/PRATdoppelEK</a>"
    "</div>",
    unsafe_allow_html=True,
)
