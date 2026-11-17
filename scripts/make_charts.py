import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

SCRATCH = "/home/blakie/.gemini/antigravity-cli/brain/9207bfc3-2551-4cda-ad91-4687664bef3f/scratch"
CHART_DIR = os.path.join(SCRATCH, "charts")
os.makedirs(CHART_DIR, exist_ok=True)

p1 = json.load(open(os.path.join(SCRATCH, "pass1_summary.json")))
p2 = json.load(open(os.path.join(SCRATCH, "pass2_summary.json")))
p3 = json.load(open(os.path.join(SCRATCH, "pass3_summary.json")))

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.8,
    "grid.color": "#EEEEEE",
    "grid.linestyle": "--",
    "grid.linewidth": 0.6,
})

NAVY = "#1B365D"
TEAL = "#008080"
CORAL = "#E05A47"
GOLD = "#D99B26"
SLATE = "#5C6B73"
BLUE = "#2B6CB0"

# 1. Chart 1: Party Flow Types (Count % vs Total USD %)
flows = p1["party_pair"]
labels = [r["flow_type"] for r in flows]
cnt_pct = [r["pct"] for r in flows]
total_usd_all = sum(r["total_usd"] for r in flows)
val_pct = [100.0 * r["total_usd"] / total_usd_all for r in flows]

x = np.arange(len(labels))
w = 0.36
fig, ax = plt.subplots(figsize=(8.5, 4.3), dpi=200)
b1 = ax.bar(x - w/2, cnt_pct, w, label="Share of Transactions (%)", color=NAVY)
b2 = ax.bar(x + w/2, val_pct, w, label="Share of Total USD Volume (%)", color=CORAL)
ax.set_xticks(x)
ax.set_xticklabels([f"{l}\n(Med: ${r['med_usd']:,.0f})" for l, r in zip(labels, flows)])
ax.set_ylabel("Percentage (%)")
ax.set_title("Payment Flow Categories: Transaction Count vs. USD Volume (N = 10,000,000)")
ax.set_ylim(0, 85)
ax.grid(axis="y")
ax.legend(frameon=True, facecolor="white")
for b in b1:
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.2, f"{b.get_height():.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold", color=NAVY)
for b in b2:
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.2, f"{b.get_height():.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold", color=CORAL)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "chart1_flow_types.png"))
plt.close()

# 2. Chart 2: Top 12 Currencies & Top 12 Ordering Countries
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.6), dpi=200)
top_cur = p1["currencies"][:12][::-1]
ax1.barh([r["CURRENCY_CODE"] for r in top_cur], [r["pct"] for r in top_cur], color=TEAL)
ax1.set_xlabel("Share of Transactions (%)")
ax1.set_title("Top 12 Payment Currencies (of 155)")
ax1.grid(axis="x")
for i, r in enumerate(top_cur):
    ax1.text(r["pct"] + 0.4, i, f"{r['pct']:.2f}%", va="center", fontsize=8.5)
ax1.set_xlim(0, 38)

top_ctry = p2["top_ord_countries"][:12][::-1]
ax2.barh([r["ord_ctry"] for r in top_ctry], [r["pct"] for r in top_ctry], color=BLUE)
ax2.set_xlabel("Share of Ordering Institutions (%)")
ax2.set_title("Top 12 Ordering Countries (BIC8)")
ax2.grid(axis="x")
for i, r in enumerate(top_ctry):
    ax2.text(r["pct"] + 0.25, i, f"{r['pct']:.2f}%", va="center", fontsize=8.5)
ax2.set_xlim(0, 19.5)

plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "chart2_currencies_countries.png"))
plt.close()

# 3. Chart 3: Routing Type & FX Conversion Distribution
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.3), dpi=200)
tx = p1["transaction_type"]
ax1.bar([r["TRANSACTION_TYPE_CODE"] for r in tx], [r["pct"] for r in tx], color=[NAVY, TEAL, GOLD])
ax1.set_ylabel("Share of Transactions (%)")
ax1.set_title("Routing Category Distribution")
ax1.set_ylim(0, 75)
ax1.grid(axis="y")
for i, r in enumerate(tx):
    ax1.text(i, r["pct"] + 1.5, f"{r['pct']:.2f}%\n(Med {r['med_dur']:.0f}s)", ha="center", va="bottom", fontsize=8.5)

fx_data = p3["fx_vs_direct_indirect"]
fx_nums = [0, 1, 2, 3, 4, 5]
for tcode, col in [("Direct", NAVY), ("Indirect", TEAL), ("Covered", GOLD)]:
    vals = []
    for n in fx_nums:
        match = [r["pct_within_type"] for r in fx_data if r["TRANSACTION_TYPE_CODE"] == tcode and r["CURRENCY_CONVERSION_COUNT"] == n]
        vals.append(match[0] if match else 0.0)
    ax2.plot(fx_nums, vals, marker="o", linewidth=2.2, label=tcode, color=col)
ax2.set_xticks(fx_nums)
ax2.set_xlabel("CURRENCY_CONVERSION_COUNT")
ax2.set_ylabel("Share Within Routing Type (%)")
ax2.set_title("FX Conversions by Routing Category")
ax2.grid(True)
ax2.legend(frameon=True, facecolor="white")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "chart3_routing_fx.png"))
plt.close()

# 4. Chart 4: Amount Buckets & Duration Buckets
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.4), dpi=200)
ab = p3["amount_buckets"]
ab_labels = [r["bucket"] for r in ab]
ab_cnt_pct = [r["pct"] for r in ab]
total_b = sum(r["total_usd_B"] for r in ab)
ab_val_pct = [100.0 * r["total_usd_B"] / total_b for r in ab]
x = np.arange(len(ab_labels))
w = 0.38
ax1.bar(x - w/2, ab_cnt_pct, w, label="Tx Count %", color=NAVY)
ax1.bar(x + w/2, ab_val_pct, w, label="USD Volume %", color=CORAL)
ax1.set_xticks(x)
ax1.set_xticklabels(ab_labels, rotation=28, ha="right", fontsize=8.5)
ax1.set_ylabel("Percentage (%)")
ax1.set_title("USD Amount Brackets: Count vs. Volume")
ax1.grid(axis="y")
ax1.legend(frameon=True, facecolor="white")

db = p3["duration_buckets"]
ax2.bar([r["dur_bucket"] for r in db], [r["pct"] for r in db], color=[TEAL, TEAL, SLATE, CORAL, GOLD])
ax2.set_ylabel("Share of Transactions (%)")
ax2.set_title("Bimodal Settlement Duration Distribution")
ax2.set_ylim(0, 38)
ax2.grid(axis="y")
for i, r in enumerate(db):
    ax2.text(i, r["pct"] + 0.8, f"{r['pct']:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "chart4_amount_duration.png"))
plt.close()

# 5. Chart 5: Temporal Patterns (DOW & Hour UTC)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=200)
dow = p2["temporal_dow"]
# Reorder Mon..Sun
order_map = {"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6}
dow_sorted = sorted(dow, key=lambda r: order_map[r["day_name"]])
colors_dow = [NAVY if r["day_name"] not in ("Sat","Sun") else CORAL for r in dow_sorted]
ax1.bar([r["day_name"] for r in dow_sorted], [r["pct"] for r in dow_sorted], color=colors_dow)
ax1.set_ylabel("Share of Transactions (%)")
ax1.set_title("Day-of-Week Activity (UTC)")
ax1.set_ylim(0, 22)
ax1.grid(axis="y")
for i, r in enumerate(dow_sorted):
    ax1.text(i, r["pct"] + 0.4, f"{r['pct']:.1f}%", ha="center", va="bottom", fontsize=8.5)

hrs = p2["temporal_hour"]
ax2.plot([r["utc_hour"] for r in hrs], [r["cnt"]/1000.0 for r in hrs], marker="o", color=TEAL, linewidth=2.2)
ax2.fill_between([r["utc_hour"] for r in hrs], [r["cnt"]/1000.0 for r in hrs], color=TEAL, alpha=0.12)
ax2.set_xticks(range(0, 24, 3))
ax2.set_xlabel("UTC Hour of Day")
ax2.set_ylabel("Transactions (Thousands)")
ax2.set_title("Hourly Transaction Volume (UTC)")
ax2.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "chart5_temporal.png"))
plt.close()

# 6. Chart 6: Anomaly Taxonomy (Count & Median USD Log-Scale)
anoms = [r for r in p1["anomaly_type"] if r["category"] != "NORMAL (NULL)"]
anoms_rev = anoms[::-1]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.3), dpi=200)
ax1.barh([r["category"] for r in anoms_rev], [r["cnt"] for r in anoms_rev], color=CORAL)
ax1.set_xlabel("Record Count (of 7,006 Anomalies)")
ax1.set_title("Anomaly Categories by Count")
ax1.grid(axis="x")
for i, r in enumerate(anoms_rev):
    ax1.text(r["cnt"] + 40, i, f"{r['cnt']:,}", va="center", fontsize=8.5)
ax1.set_xlim(0, 2950)

ax2.barh([r["category"] for r in anoms_rev], [r["med_usd"] for r in anoms_rev], color=NAVY)
ax2.set_xscale("log")
ax2.set_xlabel("Median USD Amount (Log Scale)")
ax2.set_title("Median Payment Value by Anomaly Type")
ax2.axvline(3662.58, color=TEAL, linestyle="--", linewidth=1.5, label="Normal Median ($3,663)")
ax2.legend(loc="lower right", fontsize=8.5, frameon=True, facecolor="white")
ax2.grid(axis="x")
for i, r in enumerate(anoms_rev):
    ax2.text(r["med_usd"] * 1.15, i, f"${r['med_usd']:,.0f}", va="center", fontsize=8.5)
ax2.set_xlim(50, 2000000)

plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "chart6_anomalies.png"))
plt.close()

print("All 6 charts generated successfully in", CHART_DIR)
