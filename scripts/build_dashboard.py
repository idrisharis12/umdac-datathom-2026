import json
import os
import html

REPO = "/home/blakie/Work/umdac-datathom-2026"
DATA_DIR = os.path.join(REPO, "data")
OUT_HTML = os.path.join(REPO, "dashboard", "index.html")
os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)

def load_json(name):
    with open(os.path.join(DATA_DIR, name), "r") as f:
        raw = f.read().replace("NaN", "null")
    return json.loads(raw)

p1 = load_json("pass1_summary.json")
p2 = load_json("pass2_summary.json")
p3 = load_json("pass3_summary.json")
p4 = load_json("pass4_causal_rules.json")

# Color palette
NAVY = "#0F2744"
BLUE = "#2563EB"
TEAL = "#0D9488"
CORAL = "#DC2626"
AMBER = "#D97706"
SLATE = "#64748B"

def svg_hbar(items, width=500, height=230, color=TEAL, unit="%", max_val=None, baseline=None, baseline_label=None):
    """items: list of (label, value, display_str)"""
    if not items:
        return ""
    max_lbl_len = max(len(lbl) for lbl, _, _ in items)
    ml = max(95, min(185, int(max_lbl_len * 6.3 + 14)))
    mr, mt, mb = 85, 18, 24
    pw = width - ml - mr
    ph = height - mt - mb
    mx = max_val if max_val else max(v for _, v, _ in items) * 1.15 or 1
    n = len(items)
    step = ph / n
    bh = min(22, step * 0.68)
    lines = [f'<svg viewBox="0 0 {width} {height}" class="chart-svg" xmlns="http://www.w3.org/2000/svg">']
    # Grid lines
    for frac in [0.25, 0.5, 0.75, 1.0]:
        gx = ml + pw * frac
        lines.append(f'<line x1="{gx:.1f}" y1="{mt}" x2="{gx:.1f}" y2="{mt+ph}" stroke="#E2E8F0" stroke-dasharray="3,3"/>')
        lines.append(f'<text x="{gx:.1f}" y="{height-6}" text-anchor="middle" font-size="9.5" fill="#64748B">{mx*frac:.0f}{unit}</text>')
    # Bars
    for i, (lbl, val, disp) in enumerate(items):
        cy = mt + i * step + (step - bh) / 2
        bw = max(2, (val / mx) * pw)
        c = color(lbl, i) if callable(color) else color
        lines.append(f'<g class="bar-g"><title>{html.escape(lbl)}: {html.escape(disp)}</title>')
        lines.append(f'<text x="{ml-8}" y="{cy + bh/2 + 3.5:.1f}" text-anchor="end" font-size="10.5" font-weight="600" fill="#1E293B">{html.escape(lbl)}</text>')
        lines.append(f'<rect x="{ml}" y="{cy:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{c}"/>')
        lines.append(f'<text x="{ml + bw + 6:.1f}" y="{cy + bh/2 + 3.5:.1f}" font-size="10" font-weight="600" fill="#334155">{html.escape(disp)}</text>')
        lines.append('</g>')
    if baseline is not None and baseline <= mx:
        bx = ml + (baseline / mx) * pw
        lines.append(f'<line x1="{bx:.1f}" y1="{mt-4}" x2="{bx:.1f}" y2="{mt+ph}" stroke="{CORAL}" stroke-width="1.8" stroke-dasharray="4,3"/>')
        if baseline_label:
            lines.append(f'<text x="{bx+4:.1f}" y="{mt+8}" font-size="9.5" font-weight="700" fill="{CORAL}">{html.escape(baseline_label)}</text>')
    lines.append('</svg>')
    return "\n".join(lines)

def svg_grouped_vbar(cats, s1, s2, l1, l2, c1=NAVY, c2=CORAL, width=480, height=230, unit="%"):
    ml, mr, mt, mb = 44, 16, 26, 36
    pw = width - ml - mr
    ph = height - mt - mb
    mx = max(max(s1), max(s2)) * 1.18 or 1
    n = len(cats)
    grp_w = pw / n
    bw = min(26, grp_w * 0.34)
    lines = [f'<svg viewBox="0 0 {width} {height}" class="chart-svg" xmlns="http://www.w3.org/2000/svg">']
    # Legend
    lines.append(f'<rect x="{ml}" y="4" width="10" height="10" rx="2" fill="{c1}"/><text x="{ml+14}" y="13" font-size="10" fill="#334155">{html.escape(l1)}</text>')
    lines.append(f'<rect x="{ml+155}" y="4" width="10" height="10" rx="2" fill="{c2}"/><text x="{ml+169}" y="13" font-size="10" fill="#334155">{html.escape(l2)}</text>')
    for frac in [0.25, 0.5, 0.75, 1.0]:
        gy = mt + ph * (1 - frac)
        lines.append(f'<line x1="{ml}" y1="{gy:.1f}" x2="{ml+pw}" y2="{gy:.1f}" stroke="#E2E8F0" stroke-dasharray="3,3"/>')
        lines.append(f'<text x="{ml-6}" y="{gy+3.5:.1f}" text-anchor="end" font-size="9.5" fill="#64748B">{mx*frac:.0f}{unit}</text>')
    for i, cat in enumerate(cats):
        gx = ml + i * grp_w + grp_w / 2
        h1 = (s1[i] / mx) * ph
        h2 = (s2[i] / mx) * ph
        lines.append(f'<g class="bar-g"><title>{cat}: {l1}={s1[i]:.1f}{unit}, {l2}={s2[i]:.1f}{unit}</title>')
        lines.append(f'<rect x="{gx - bw - 2:.1f}" y="{mt + ph - h1:.1f}" width="{bw:.1f}" height="{h1:.1f}" rx="2" fill="{c1}"/>')
        lines.append(f'<text x="{gx - bw/2 - 2:.1f}" y="{mt + ph - h1 - 4:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{c1}">{s1[i]:.1f}%</text>')
        lines.append(f'<rect x="{gx + 2:.1f}" y="{mt + ph - h2:.1f}" width="{bw:.1f}" height="{h2:.1f}" rx="2" fill="{c2}"/>')
        lines.append(f'<text x="{gx + bw/2 + 2:.1f}" y="{mt + ph - h2 - 4:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{c2}">{s2[i]:.1f}%</text>')
        lines.append(f'<text x="{gx:.1f}" y="{height - 16}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1E293B">{html.escape(cat)}</text>')
        lines.append('</g>')
    lines.append('</svg>')
    return "\n".join(lines)

def svg_vbar(items, width=480, height=225, color=NAVY, unit="%"):
    ml, mr, mt, mb = 44, 16, 18, 34
    pw = width - ml - mr
    ph = height - mt - mb
    mx = max(v for _, v, _ in items) * 1.18 or 1
    n = len(items)
    step = pw / n
    bw = min(38, step * 0.62)
    lines = [f'<svg viewBox="0 0 {width} {height}" class="chart-svg" xmlns="http://www.w3.org/2000/svg">']
    for frac in [0.25, 0.5, 0.75, 1.0]:
        gy = mt + ph * (1 - frac)
        lines.append(f'<line x1="{ml}" y1="{gy:.1f}" x2="{ml+pw}" y2="{gy:.1f}" stroke="#E2E8F0" stroke-dasharray="3,3"/>')
        lines.append(f'<text x="{ml-6}" y="{gy+3.5:.1f}" text-anchor="end" font-size="9.5" fill="#64748B">{mx*frac:.0f}{unit}</text>')
    for i, (lbl, val, disp) in enumerate(items):
        cx = ml + i * step + step / 2
        bh = max(2, (val / mx) * ph)
        c = color(lbl, i) if callable(color) else color
        lines.append(f'<g class="bar-g"><title>{html.escape(lbl)}: {html.escape(disp)}</title>')
        lines.append(f'<rect x="{cx - bw/2:.1f}" y="{mt + ph - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{c}"/>')
        lines.append(f'<text x="{cx:.1f}" y="{mt + ph - bh - 4:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#1E293B">{html.escape(disp)}</text>')
        lines.append(f'<text x="{cx:.1f}" y="{height - 14}" text-anchor="middle" font-size="10" font-weight="600" fill="#334155">{html.escape(lbl)}</text>')
        lines.append('</g>')
    lines.append('</svg>')
    return "\n".join(lines)

def svg_multiline(xs, series_list, width=480, height=225, x_label="", y_unit="%"):
    """series_list: [(name, color, values)]"""
    ml, mr, mt, mb = 44, 18, 26, 34
    pw = width - ml - mr
    ph = height - mt - mb
    mx = max(max(vals) for _, _, vals in series_list) * 1.15 or 1
    n = len(xs)
    lines = [f'<svg viewBox="0 0 {width} {height}" class="chart-svg" xmlns="http://www.w3.org/2000/svg">']
    for idx, (name, col, _) in enumerate(series_list):
        lx = ml + idx * 115
        lines.append(f'<line x1="{lx}" y1="9" x2="{lx+14}" y2="9" stroke="{col}" stroke-width="2.5"/><text x="{lx+18}" y="12.5" font-size="10" font-weight="600" fill="#334155">{html.escape(name)}</text>')
    for frac in [0.25, 0.5, 0.75, 1.0]:
        gy = mt + ph * (1 - frac)
        lines.append(f'<line x1="{ml}" y1="{gy:.1f}" x2="{ml+pw}" y2="{gy:.1f}" stroke="#E2E8F0" stroke-dasharray="3,3"/>')
        lines.append(f'<text x="{ml-6}" y="{gy+3.5:.1f}" text-anchor="end" font-size="9.5" fill="#64748B">{mx*frac:.0f}{y_unit}</text>')
    for i, xl in enumerate(xs):
        px = ml + (i / (n - 1)) * pw
        lines.append(f'<text x="{px:.1f}" y="{height-14}" text-anchor="middle" font-size="10" fill="#475569">{html.escape(str(xl))}</text>')
    for name, col, vals in series_list:
        pts = []
        for i, v in enumerate(vals):
            px = ml + (i / (n - 1)) * pw
            py = mt + ph - (v / mx) * ph
            pts.append((px, py, v))
        d = " ".join(f"{'M' if i==0 else 'L'}{px:.1f},{py:.1f}" for i, (px, py, _) in enumerate(pts))
        lines.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.4"/>')
        for i, (px, py, v) in enumerate(pts):
            lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{col}" stroke="#FFF" stroke-width="1"><title>{name} ({xs[i]}): {v:.2f}{y_unit}</title></circle>')
    if x_label:
        lines.append(f'<text x="{ml + pw/2:.1f}" y="{height-2}" text-anchor="middle" font-size="9.5" fill="#64748B">{html.escape(x_label)}</text>')
    lines.append('</svg>')
    return "\n".join(lines)

# Prepare Dashboard Data
# D1: Party Flow
flows = p1["party_pair"]
total_usd_all = p1["overview"]["sum_usd"]
d1_c1 = svg_grouped_vbar(
    [r["flow_type"] for r in flows],
    [r["pct"] for r in flows],
    [100 * r["total_usd"] / total_usd_all for r in flows],
    "Tx Count Share (%)", "USD Volume Share (%)", NAVY, CORAL
)
d1_c2 = svg_hbar(
    [(r["flow_type"], r["med_usd"], f"${r['med_usd']:,.2f}") for r in flows],
    color=TEAL, unit=""
)

# D2: Currencies & Home Currency
top_cur = p1["currencies"][:10]
d2_c1 = svg_hbar(
    [(r["CURRENCY_CODE"], r["pct"], f"{r['pct']:.2f}% (${r['total_usd']/1e9:.1f}B)") for r in top_cur],
    color=NAVY, max_val=38
)
home_cur = p4["currency_home_match"][:9]
d2_c2 = svg_hbar(
    [(r["ord_ctry"], r["pct_ord_home_cur"], f"{r['pct_ord_home_cur']:.1f}%") for r in home_cur],
    color=TEAL, max_val=105, baseline=50, baseline_label="50% Baseline"
)

# D3: Geography & Timezones
tz = p4["timezone_peak_by_country"]
d3_c1 = svg_grouped_vbar(
    [r["ord_ctry"] for r in tz],
    [r["pct_00_07_asia"] for r in tz],
    [r["pct_16_23_us"] for r in tz],
    "00-07 UTC (APAC Hrs)", "16-23 UTC (US Hrs)", TEAL, BLUE
)
dow_order = {"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6}
dow_sorted = sorted(p2["temporal_dow"], key=lambda r: dow_order[r["day_name"]])
d3_c2 = svg_vbar(
    [(r["day_name"], r["pct"], f"{r['pct']:.1f}%") for r in dow_sorted],
    color=lambda lbl, _: CORAL if lbl in ("Sat", "Sun") else NAVY
)

# D4: Routing & FX
tx = p1["transaction_type"]
d4_c1 = svg_vbar(
    [(r["TRANSACTION_TYPE_CODE"], r["pct"], f"{r['pct']:.1f}%") for r in tx],
    color=lambda lbl, _: NAVY if lbl == "Direct" else (TEAL if lbl == "Indirect" else AMBER)
)
fx_xs = [0, 1, 2, 3, 4, 5]
fx_series = []
for tcode, col in [("Direct", NAVY), ("Indirect", TEAL), ("Covered", AMBER)]:
    vals = []
    for n in fx_xs:
        m = [r["pct_within_type"] for r in p3["fx_vs_direct_indirect"] if r["TRANSACTION_TYPE_CODE"] == tcode and r["CURRENCY_CONVERSION_COUNT"] == n]
        vals.append(m[0] if m else 0.0)
    fx_series.append((tcode, col, vals))
d4_c2 = svg_multiline(fx_xs, fx_series, x_label="CURRENCY_CONVERSION_COUNT")

# D5: Amount & Outliers
ab = p3["amount_buckets"]
d5_c1 = svg_grouped_vbar(
    [r["bucket"].replace(" - ", "-") for r in ab],
    [r["pct"] for r in ab],
    [100 * r["total_usd_B"] / 972.041 for r in ab],
    "Tx Count %", "USD Volume %", NAVY, CORAL
)
# Normal vs Fat Finger impact
d5_c2 = svg_hbar([
    ("Normal (99.93%)", 795.425, "$795.4B (Mean $79.6K)"),
    ("Fat Finger (0.019%)", 175.137, "$175.1B (Mean $90.3M)"),
    ("Other Anomalies (0.05%)", 1.479, "$1.5B"),
], color=lambda lbl, _: CORAL if "Fat" in lbl else NAVY, unit="B", max_val=900)

# D6: Duration & Hop Law
db = p3["duration_buckets"]
d6_c1 = svg_vbar(
    [(r["dur_bucket"], r["pct"], f"{r['pct']:.1f}%") for r in db],
    color=lambda lbl, _: TEAL if lbl in ("< 30s", "30s - 2m") else (CORAL if lbl == "10m - 1h" else SLATE)
)
part_avg = [(str(r["PARTICIPANT_COUNT"]) + " hops", r["avg_dur"], f"{r['avg_dur']:.0f}s") for r in p1["participant_counts"][:6]]
d6_c2 = svg_hbar(part_avg, color=BLUE, unit="s", max_val=2000)

# D7: Anomalies
anoms = [r for r in p1["anomaly_type"] if r["category"] != "NORMAL (NULL)"]
d7_c1 = svg_hbar(
    [(r["category"].replace("ACCOUNT_REPLACEMENT_SCAM", "ACCT REPLACEMENT").replace("_", " "), r["cnt"], f"{r['cnt']:,} ({100*r['cnt']/7006:.1f}%)") for r in anoms],
    color=CORAL, unit="", max_val=3100
)
d7_c2 = svg_hbar(
    [(r["category"].replace("ACCOUNT_REPLACEMENT_SCAM", "ACCT REPLACEMENT").replace("_", " "), r["med_dur"], f"{r['med_dur']:.0f}s") for r in anoms],
    color=NAVY, unit="s", max_val=1350, baseline=56, baseline_label="Normal Med: 56s"
)

# D8: Tokens & Details
toks = p3["token_tag_counts_sample"][:10]
d8_c1 = svg_hbar(
    [(r["tag"] + ">", r["cnt"] / 1000.0, f"{r['cnt']:,}") for r in toks],
    color=TEAL, unit="K", max_val=620
)
d8_c2 = svg_hbar([
    ("Pure Single-Type Accts", 100.0, "391,132 / 391,132 (100%)"),
    ("Continuous BIC Paths (Y)", 92.33, "9,232,796 (92.33%)"),
    ("Cross-Border Flows", 92.89, "9,288,884 (92.89%)"),
    ("Zero-Null Schema Cols", 90.48, "19 / 21 Columns (0 NULLs)"),
], color=NAVY, max_val=115)

dashboards = [
    {
        "id": "d1", "nav": "1. Party Flows",
        "title": "Dashboard 1: Party Flow Categories (B2C, B2B, C2C, C2B)",
        "subtitle": "Feature Group: ORDERING_TYPE, BENEFICIARY_TYPE & ORDERING_ACCOUNT (N = 10,000,000)",
        "kpis": [("B2C Count Share", "56.04%", "5.60M payroll/payout wires"), ("B2B Value Share", "72.54%", "$705.14B of $972.04B total"), ("B2B vs C2C Median", "49.4x", "$22,888 vs. $463"), ("Account Role Purity", "100.0%", "391,132 / 391,132 pure")],
        "c1_title": "B2C Dominates Transaction Count (56%), While B2B Dominates USD Value (72.5%)", "c1": d1_c1,
        "c2_title": "Median Payment Value by Party Flow (Baseline: Overall Median $3,662)", "c2": d1_c2,
        "rule": "Rule 1 & 6: Every ORDERING_ACCOUNT has an immutable entity type (100% pure). B2B tickets are ~50x larger than C2C, yet routing mode (~63.2% Direct) is statistically independent of party flow.",
        "econ": "Economic Logic: Corporates initiate high-value supplier settlements (B2B) and bulk consumer disbursements (B2C). Routing topology depends on bank-corridor agreements, not customer ticket size.",
        "rejected": "Rejected Hypothesis: 'High-value B2B wires use Covered/Indirect routing more often than C2C.' Disproved: Direct share is 63.22% (B2B), 63.23% (B2C), 63.19% (C2B), 63.28% (C2C)."
    },
    {
        "id": "d2", "nav": "2. Currencies",
        "title": "Dashboard 2: Currency Distribution & Home-Currency Dominance",
        "subtitle": "Feature Group: CURRENCY_CODE across 155 ISO 4217 Currencies (N = 10,000,000)",
        "kpis": [("Distinct Currencies", "155", "ISO 4217 codes"), ("EUR + USD Count", "49.02%", "31.99% EUR + 17.03% USD"), ("EUR + USD Volume", "59.46%", "$577.98B combined"), ("Home-Currency Rate", "84-94.5%", "Top 10 ordering countries")],
        "c1_title": "EUR (32.0%) and USD (17.0%) Account for Nearly Half of All Payment Instructions", "c1": d2_c1,
        "c2_title": "83.8% to 94.5% of Payments Are Initiated in the Ordering Country's Home Currency", "c2": d2_c2,
        "rule": "Rule 2: When an ordering institution is in country C, 83.8%-94.5% of its outgoing payments use C's domestic currency (DE 94.5% EUR, FR 94.0% EUR, US 90.5% USD, CH 88.8% CHF).",
        "econ": "Economic Logic: Exporters and multinational corporates invoice and fund cross-border wires in their primary operating currency, pushing FX conversion downstream to correspondent/beneficiary banks.",
        "rejected": "Note: Synthetic country sizes are randomized per Swift's privacy design, but home-currency invoicing behavior faithfully mirrors real-world corporate treasury practice."
    },
    {
        "id": "d3", "nav": "3. Geography & Time",
        "title": "Dashboard 3: Geographic Corridors & Temporal Banking Cycles",
        "subtitle": "Feature Group: EPOCH_SECONDS & BIC8 Country Codes (Apr 30 - Jul 31, 2023 UTC)",
        "kpis": [("Cross-Border Share", "92.89%", "9.29M cross-border wires"), ("Top Corridor", "US -> US", "385,598 wires (3.86%)"), ("Weekday vs Weekend", "4.2x", "18.3% Mon/Fri vs 4.35% Sat"), ("Same-BIC Transfers", "0.024%", "2,387 internal book transfers")],
        "c1_title": "Ordering Countries Peak During Local Business Hours (APAC 00-07 UTC vs. US 16-23 UTC)", "c1": d3_c1,
        "c2_title": "Global Payment Volume Drops ~75% on Saturdays (4.35%) & Sundays (6.84%)", "c2": d3_c2,
        "rule": "Rule 3: Timestamp generation is modulated by ordering-country timezone (APAC 41-46% in 00-07 UTC; EU 41-43% in 08-15 UTC; US 46.7% in 16-23 UTC) and banking-calendar weekend closures.",
        "econ": "Economic Logic: Real-time gross settlement (RTGS) systems (TARGET2, Fedwire, CHIPS) close on weekends and operate during regional business windows, creating the 15:00-17:00 UTC EU-US overlap peak.",
        "rejected": "Data Scope: Covers ~92 days (2023-04-30 11:22 UTC to 2023-07-31 09:56 UTC), with June accounting for 40.50% of volume."
    },
    {
        "id": "d4", "nav": "4. Routing & FX",
        "title": "Dashboard 4: Routing Topology, Continuity & FX Conversions",
        "subtitle": "Feature Group: TRANSACTION_TYPE_CODE, PARTICIPANT_COUNT, CURRENCY_CONVERSION_COUNT, CONTINUITY_QFLAG",
        "kpis": [("Direct Route Share", "63.23%", "Strictly 2 participants"), ("Direct FX Ceiling", "0 or 1", "0.00% have >=2 FX steps"), ("Indirect/Covered Peak", "2 FX", "~55.5% have 2 conversions"), ("Discontinuous Paths", "7.67%", "767,204 contain '...'")],
        "c1_title": "Direct Bilateral Routing Accounts for 63.2% of Traffic vs. 32.6% Indirect & 4.2% Covered", "c1": d4_c1,
        "c2_title": "Direct Routes Cap FX at 1 Step, While Indirect & Covered Peak Sharply at 2 FX Steps", "c2": d4_c2,
        "rule": "Rule 5: Direct = 2 participants and FX in {0, 1} (100% deterministic). Indirect (32.61%) & Covered (4.16%) average 3.582 participants, peak at 2 FX conversions, and reach up to 22 hops / 17 FX steps.",
        "econ": "Economic Logic: Direct Nostro/Vostro accounts settle bilaterally with at most one currency conversion, whereas multi-bank correspondent chains introduce intermediate clearing legs and double-FX conversions.",
        "rejected": "Continuity Coupling: Discontinuous paths (CONTINUITY_QFLAG='N') occur at 12.3% in Indirect/Covered vs. only 5.0% in Direct."
    },
    {
        "id": "d5", "nav": "5. Amounts & Outliers",
        "title": "Dashboard 5: Payment Value Distribution & Fat-Finger Distortion",
        "subtitle": "Feature Group: USD_AMOUNT ($0.01 to $15.66B; Aggregate $972.04B)",
        "kpis": [("Median USD Amount", "$3,661.90", "IQR: $634 - $19,960"), ("Mean USD Amount", "$97,204.10", "26.5x median (heavy tail)"), (">= $10M Wires", "0.08%", "7,586 rows = 35.0% of value"), ("Fat-Finger Impact", "$175.14B", "18.02% of total from 1,940 rows")],
        "c1_title": "Extreme Right-Skew: 0.08% of Payments (>=$10M) Generate 35.0% of Total USD Volume", "c1": d5_c1,
        "c2_title": "Just 1,940 FAT_FINGER_MISTAKE Rows (0.019%) Account for 18.02% ($175.1B) of Dataset Value", "c2": d5_c2,
        "rule": "Rule 8a: Normal payments follow a log-normal-like retail/corporate mix (median $3,663), but FAT_FINGER_MISTAKE injects 71x-1000x magnitude errors (median $260,241; mean $90.28M) without altering duration.",
        "econ": "Economic Logic: Comma/decimal-separator typos in manual wire entry create massive outlier spikes that distort aggregate volume metrics if not isolated during data cleaning.",
        "rejected": "Data Integrity Action: Always filter or stratify by ANOMALY_TYPE != 'FAT_FINGER_MISTAKE' before estimating normal corridor ticket sizes."
    },
    {
        "id": "d6", "nav": "6. Settlement Latency",
        "title": "Dashboard 6: Bimodal Settlement Duration & Hop-Count Law",
        "subtitle": "Feature Group: TOTAL_DURATION (2s to 21,649s; Median 56s; Mean 771.5s)",
        "kpis": [("Fast STP (< 2 min)", "53.92%", "30.35% <30s + 23.57% 30s-2m"), ("Slow Cluster (10m-1h)", "28.53%", "Second modal peak"), ("Per-Hop Latency", "+~200s", "Linear scaling per bank"), ("Direct vs Indirect Med", "39s vs 281s", "7.2x faster median")],
        "c1_title": "Bimodal Settlement: 53.9% Clear Under 2 Minutes vs. a 28.5% Cluster at 10m-1h", "c1": d6_c1,
        "c2_title": "Mean Settlement Duration Scales Linearly by ~200 Seconds per Participant Bank Hop", "c2": d6_c2,
        "rule": "Rule 4: PARTICIPANT_COUNT—not FX count—governs TOTAL_DURATION: mean latency rises linearly (+~200s/hop) from 663s (2 hops) -> 841s (3) -> 1,042s (4) -> 1,242s (5) -> 1,437s (6) -> 1,649s (7).",
        "econ": "Economic Logic: Straight-through processing (STP) Direct wires clear in seconds, while each intermediary bank adds sanctions screening, batch cut-off, and reconciliation latency.",
        "rejected": "Rejected Hypothesis: 'More FX conversions cause longer settlement duration.' Disproved: Within 4-hop payments, median duration is 429s (0 FX), 418s (1 FX), 418s (2 FX), 418s (3 FX)."
    },
    {
        "id": "d7", "nav": "7. Anomalies & Fraud",
        "title": "Dashboard 7: Anomaly Taxonomy & Role-Gated Fraud Forensics",
        "subtitle": "Feature Group: ANOMALY_TYPE (7,006 Labeled Records = 0.0701% across 6 Categories)",
        "kpis": [("Total Anomalies", "7,006", "0.0701% of 10M rows"), ("Romance Scam Purity", "100% C2*", "500 senders -> 378 mules"), ("CEO Scam Purity", "100% B2*", "98.7% cross-border, $1.38M avg"), ("Undocumented Class", "317 rows", "CUSTOMER_RECALL (not in PDF)")],
        "c1_title": "6 Anomaly Categories: ROMANCE_SCAM (35.3%) and FAT_FINGER_MISTAKE (27.7%) Lead Counts", "c1": d7_c1,
        "c2_title": "Social-Engineering Scams Exhibit 10x-20x Longer Duration vs. Normal Baseline (56s)", "c2": d7_c2,
        "rule": "Rule 7, 8b & 9: ROMANCE_SCAM is 100% Consumer-originated (500 senders -> 378 receivers); CEO_SCAM is 100% Business-originated; DUPLICATE_PAYMENT replays 185 tuples (median 1,099s gap); CUSTOMER_RECALL has 11.04% path gaps.",
        "econ": "Economic Logic: Fraud topologies mirror real-world typologies—romance victims send repeated small wires to mule networks, BEC/CEO fraud targets corporate treasuries, and recalls surface on opaque chains.",
        "rejected": "Critical Discovery: CUSTOMER_RECALL (317 rows) exists in the CSV despite being omitted from the official Case Study PDF Appendix."
    },
    {
        "id": "d8", "nav": "8. Text & Tokens",
        "title": "Dashboard 8: Remittance Text Tokens & Structural Integrity",
        "subtitle": "Feature Group: ORDERING_TOKENS, BENEFICIARY_TOKENS & Schema Integrity (200K Reservoir Sample)",
        "kpis": [("Token Tag Families", "19", "Extracted across 200K sample"), ("Top Pattern Tag", "<chr:...>", "529,061 character masks"), ("IBAN Detections", "200,449", "Standardized <iban:22>"), ("Zero-Null Columns", "19 / 21", "100% populated fields")],
        "c1_title": "Top 10 Semantic Token Tags Extracted from Party Details (200,000-Row Sample)", "c1": d8_c1,
        "c2_title": "Dataset Structural Integrity & Graph Invariants Across All 10,000,000 Records", "c2": d8_c2,
        "rule": "Schema & Tokenization Rule: Raw multiline party text (expanding 10M rows to 83.81M physical lines) is deterministically masked into 19 semantic tag classes (<chr:>, <street:>, <city:CC:N>, <iban:N>, <business:>, <last_name:> ).",
        "econ": "Economic Logic: Engineered *_TOKENS preserve structural formatting signals (IBAN presence, corporate keywords, address completeness) needed for AML/sanctions screening without exposing PII.",
        "rejected": "Engineering Warning: Naive line-splitting tools (awk/wc) break on embedded newlines inside quoted *_DETAILS fields; always use an RFC-4180 CSV parser."
    }
]

nav_links = "\n".join(
    f'<button class="nav-btn{" active" if i==0 else ""}" data-target="{d["id"]}" onclick="showDash(\'{d["id"]}\', this)">{html.escape(d["nav"])}</button>'
    for i, d in enumerate(dashboards)
)

pages_html = []
for i, d in enumerate(dashboards):
    kpis_html = "\n".join(
        f'<div class="kpi"><div class="kpi-lbl">{html.escape(k[0])}</div><div class="kpi-val">{html.escape(k[1])}</div><div class="kpi-sub">{html.escape(k[2])}</div></div>'
        for k in d["kpis"]
    )
    pages_html.append(f"""
    <section id="{d['id']}" class="dash-page{' active' if i==0 else ''}">
      <div class="dash-header">
        <div>
          <div class="dash-tag">UMDAC DATATHON 2026 &bull; SWIFT PAYMENTS</div>
          <h1>{html.escape(d['title'])}</h1>
          <div class="dash-sub">{html.escape(d['subtitle'])}</div>
        </div>
        <div class="page-badge">Dashboard {i+1} of {len(dashboards)}</div>
      </div>

      <div class="kpi-grid">{kpis_html}</div>

      <div class="charts-grid">
        <div class="card">
          <div class="card-title">{html.escape(d['c1_title'])}</div>
          <div class="card-body">{d['c1']}</div>
        </div>
        <div class="card">
          <div class="card-title">{html.escape(d['c2_title'])}</div>
          <div class="card-body">{d['c2']}</div>
        </div>
      </div>

      <div class="insights-grid">
        <div class="insight-box rule-box">
          <div class="box-hdr">Reconstructed Causal Rule</div>
          <p>{html.escape(d['rule'])}</p>
        </div>
        <div class="insight-box econ-box">
          <div class="box-hdr">Real-World Economic Reasoning</div>
          <p>{html.escape(d['econ'])}</p>
        </div>
        <div class="insight-box rej-box">
          <div class="box-hdr">Verification / Caveat</div>
          <p>{html.escape(d['rejected'])}</p>
        </div>
      </div>
    </section>
    """)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Swift UMDAC Datathon 2026 — Interactive &amp; Printable Dashboards</title>
<style>
  :root {{
    --navy: #0F2744;
    --teal: #0D9488;
    --coral: #DC2626;
    --bg: #F1F5F9;
    --card: #FFFFFF;
    --border: #E2E8F0;
    --text: #1E293B;
    --muted: #64748B;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); display: flex; min-height: 100vh; }}
  .sidebar {{ width: 235px; background: var(--navy); color: #FFF; padding: 20px 14px; display: flex; flex-direction: column; gap: 6px; flex-shrink: 0; position: sticky; top: 0; height: 100vh; }}
  .brand {{ font-size: 15px; font-weight: 800; letter-spacing: 0.3px; margin-bottom: 4px; color: #F8FAFC; }}
  .brand-sub {{ font-size: 11px; color: #94A3B8; margin-bottom: 14px; line-height: 1.4; }}
  .nav-btn {{ background: transparent; border: none; color: #CBD5E1; text-align: left; padding: 9px 12px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.15s; }}
  .nav-btn:hover {{ background: rgba(255,255,255,0.08); color: #FFF; }}
  .nav-btn.active {{ background: var(--teal); color: #FFF; }}
  .sidebar-footer {{ margin-top: auto; display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.12); }}
  .action-btn {{ background: #2563EB; color: #FFF; border: none; padding: 9px 12px; border-radius: 6px; font-size: 12.5px; font-weight: 700; cursor: pointer; }}
  .action-btn.sec {{ background: rgba(255,255,255,0.12); }}
  .main {{ flex: 1; padding: 22px 28px; max-width: 1220px; margin: 0 auto; }}
  .dash-page {{ display: none; background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 24px; }}
  .dash-page.active, body.show-all .dash-page {{ display: block; }}
  .dash-header {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid var(--navy); padding-bottom: 10px; margin-bottom: 14px; }}
  .dash-tag {{ font-size: 10px; font-weight: 800; color: var(--teal); letter-spacing: 0.8px; margin-bottom: 3px; }}
  .dash-header h1 {{ font-size: 20px; color: var(--navy); font-weight: 800; }}
  .dash-sub {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
  .page-badge {{ background: #E2E8F0; color: var(--navy); font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 999px; white-space: nowrap; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 14px; }}
  .kpi {{ background: #F8FAFC; border: 1px solid var(--border); border-left: 4px solid var(--teal); border-radius: 6px; padding: 10px 12px; }}
  .kpi-lbl {{ font-size: 10.5px; font-weight: 700; color: var(--muted); text-transform: uppercase; }}
  .kpi-val {{ font-size: 20px; font-weight: 800; color: var(--navy); margin: 2px 0; }}
  .kpi-sub {{ font-size: 11px; color: #475569; }}
  .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }}
  .card {{ border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; background: #FFF; }}
  .card-title {{ font-size: 12.5px; font-weight: 700; color: var(--navy); margin-bottom: 8px; line-height: 1.3; }}
  .chart-svg {{ width: 100%; height: auto; display: block; }}
  .bar-g:hover rect {{ opacity: 0.82; }}
  .insights-grid {{ display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 12px; }}
  .insight-box {{ border-radius: 6px; padding: 10px 12px; font-size: 11.5px; line-height: 1.45; border: 1px solid var(--border); }}
  .rule-box {{ background: #EFF6FF; border-left: 4px solid #2563EB; }}
  .econ-box {{ background: #F0FDFA; border-left: 4px solid var(--teal); }}
  .rej-box {{ background: #FEF2F2; border-left: 4px solid var(--coral); }}
  .box-hdr {{ font-size: 10.5px; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; color: var(--navy); }}
  @media print {{
    @page {{ size: A4 landscape; margin: 8mm; }}
    body {{ background: #FFF; display: block; }}
    .sidebar {{ display: none !important; }}
    .main {{ padding: 0; max-width: none; }}
    .dash-page {{ display: block !important; border: none; box-shadow: none; padding: 8px 10px; margin: 0; page-break-after: always; break-after: page; }}
    .dash-page:last-child {{ page-break-after: auto; break-after: auto; }}
  }}
</style>
</head>
<body>
  <aside class="sidebar">
    <div class="brand">SWIFT UMDAC 2026</div>
    <div class="brand-sub">10,000,000 Rows &bull; $972.04B<br>8 Feature-Group Dashboards</div>
    {nav_links}
    <div class="sidebar-footer">
      <button class="action-btn sec" onclick="toggleAll(this)">Show All 8 Dashboards</button>
      <button class="action-btn" onclick="window.print()">Export 8-Page PDF</button>
    </div>
  </aside>
  <main class="main">
    {"".join(pages_html)}
  </main>
<script>
  function showDash(id, btn) {{
    document.body.classList.remove('show-all');
    document.querySelectorAll('.dash-page').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    if (btn) btn.classList.add('active');
  }}
  function toggleAll(btn) {{
    const on = document.body.classList.toggle('show-all');
    btn.textContent = on ? 'Single Dashboard View' : 'Show All 8 Dashboards';
  }}
</script>
</body>
</html>
"""

with open(OUT_HTML, "w") as f:
    f.write(full_html)

print("Built interactive & printable dashboard at:", OUT_HTML)
