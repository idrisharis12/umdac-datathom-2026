import json
import os
import html

REPO = "/home/blakie/Work/umdac-datathom-2026"
DATA_DIR = os.path.join(REPO, "data")
OUT_HTML = "/home/blakie/.gemini/antigravity-cli/brain/9207bfc3-2551-4cda-ad91-4687664bef3f/scratch/master_guide.html"
OUT_PDF = os.path.join(REPO, "UMDAC_Datathon_2026_Master_Guide_and_Complete_Analysis.pdf")

def load_json(name):
    with open(os.path.join(DATA_DIR, name), "r") as f:
        return json.loads(f.read().replace("NaN", "null"))

p1 = load_json("pass1_summary.json")
p2 = load_json("pass2_summary.json")
p3 = load_json("pass3_summary.json")
p4 = load_json("pass4_causal_rules.json")

fmt_i = lambda n: f"{int(n):,}"
fmt_usd = lambda n: f"${float(n):,.2f}"
fmt_b = lambda n: f"${float(n)/1e9:,.2f}B"

flow_rows = "".join(
    f"<tr><td><b>{r['flow_type']}</b></td><td class='num'>{fmt_i(r['cnt'])}</td><td class='num'>{r['pct']:.2f}%</td>"
    f"<td class='num'>{fmt_usd(r['med_usd'])}</td><td class='num'>{fmt_usd(r['avg_usd'])}</td>"
    f"<td class='num'>{fmt_b(r['total_usd'])}</td><td class='num'>{100*r['total_usd']/p1['overview']['sum_usd']:.2f}%</td></tr>"
    for r in p1["party_pair"]
)

cur_rows = "".join(
    f"<tr><td class='num'>{i+1}</td><td><b>{r['CURRENCY_CODE']}</b></td><td class='num'>{fmt_i(r['cnt'])}</td>"
    f"<td class='num'>{r['pct']:.2f}%</td><td class='num'>{fmt_usd(r['med_usd'])}</td>"
    f"<td class='num'>{fmt_usd(r['avg_usd'])}</td><td class='num'>{fmt_b(r['total_usd'])}</td></tr>"
    for i, r in enumerate(p1["currencies"][:12])
)

anom_rows = ""
for r in p1["anomaly_type"]:
    if r["category"] == "NORMAL (NULL)":
        continue
    fx = next((x for x in p3["anomaly_fx_and_crossborder"] if x["anomaly"] == r["category"]), {})
    anom_rows += (
        f"<tr><td><b>{r['category']}</b></td><td class='num'>{fmt_i(r['cnt'])}</td>"
        f"<td class='num'>{100*r['cnt']/7006:.1f}%</td><td class='num'>{fmt_usd(r['med_usd'])}</td>"
        f"<td class='num'>{fmt_usd(r['avg_usd'])}</td><td class='num'>{r['med_dur']:.0f}s</td>"
        f"<td class='num'>{fx.get('pct_crossborder', 0):.2f}%</td></tr>"
    )

html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>UMDAC Datathon 2026 — Master Guide &amp; Complete Analysis</title>
<style>
  @page {{ size: A4 portrait; margin: 14mm 15mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #1E293B; font-size: 9.8pt; line-height: 1.45; margin: 0; }}
  .cover {{ background: linear-gradient(135deg, #0F2744 0%, #1E3A5F 100%); color: #FFF; padding: 26px 28px; border-radius: 8px; margin-bottom: 16px; }}
  .cover-tag {{ font-size: 8.5pt; font-weight: 800; letter-spacing: 1px; color: #5EEAD4; text-transform: uppercase; margin-bottom: 6px; }}
  .cover h1 {{ font-size: 21pt; margin: 0 0 8px 0; line-height: 1.2; }}
  .cover p {{ font-size: 10pt; color: #CBD5E1; margin: 0; }}
  h2 {{ font-size: 13pt; color: #0F2744; border-bottom: 2px solid #0F2744; padding-bottom: 4px; margin: 18px 0 8px 0; page-break-after: avoid; }}
  h3 {{ font-size: 10.5pt; color: #0D9488; margin: 12px 0 5px 0; page-break-after: avoid; }}
  p {{ margin: 0 0 8px 0; }}
  ul, ol {{ margin: 4px 0 10px 0; padding-left: 20px; }}
  li {{ margin-bottom: 4px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 8px 0 12px 0; font-size: 8.8pt; page-break-inside: avoid; }}
  th {{ background: #0F2744; color: #FFF; text-align: left; padding: 6px 8px; font-weight: 700; }}
  th.num, td.num {{ text-align: right; }}
  td {{ padding: 5px 8px; border-bottom: 1px solid #E2E8F0; vertical-align: top; }}
  tr:nth-child(even) td {{ background: #F8FAFC; }}
  .callout {{ background: #EFF6FF; border-left: 4px solid #2563EB; padding: 9px 12px; border-radius: 4px; margin: 10px 0; font-size: 9.2pt; page-break-inside: avoid; }}
  .warn {{ background: #FEF2F2; border-left: 4px solid #DC2626; padding: 9px 12px; border-radius: 4px; margin: 10px 0; font-size: 9.2pt; page-break-inside: avoid; }}
  .teal {{ background: #F0FDFA; border-left: 4px solid #0D9488; padding: 9px 12px; border-radius: 4px; margin: 10px 0; font-size: 9.2pt; page-break-inside: avoid; }}
  .page-break {{ page-break-before: always; }}
  code {{ background: #F1F5F9; padding: 1px 4px; border-radius: 3px; font-size: 8.5pt; color: #0F2744; }}
</style>
</head>
<body>

<div class="cover">
  <div class="cover-tag">UMDAC Datathon 2026 &bull; Swift Case Study &bull; Complete Reference</div>
  <h1>Master Guide: Competition Rules, Action Checklist, Dataset Dictionary &amp; Reverse-Engineered Logic</h1>
  <p>Everything from the Official Handbook, Rules &amp; Regulations, Submission Format, Judging Rubric, and Full 10,000,000-Row Empirical Analysis</p>
</div>

<h2>1. Competition Overview &amp; Official Schedule</h2>
<p>The <b>UMDAC Datathon 2026</b> (Universiti Malaya Data Analytics Club) in collaboration with <b>SWIFT</b> challenges university teams (1-3 members) to reverse-engineer the hard-coded business rules, causal relationships, and economic logic behind a 10M-row synthetic cross-border payment dataset. Unlike coding-only contests, judges reward <b>causal insight quality and real-world economic reasoning</b> over model complexity.</p>

<table>
  <tr><th>Date / Time (UTC+8)</th><th>Milestone</th><th>Mode / Details</th></tr>
  <tr><td>27 Oct - 9 Nov 2026</td><td>Registration</td><td>Online (teams of 1-3 university students)</td></tr>
  <tr><td>13 Nov 2026, 11:50 AM</td><td>Preliminary Round Start</td><td>Opening Ceremony, Problem Statement &amp; Dataset Release (144-hour sprint)</td></tr>
  <tr><td>17 Nov 2026</td><td>Online Workshop 1</td><td>Data Science &amp; Analytics hands-on session (MS Teams / Discord)</td></tr>
  <tr><td><b>19 Nov 2026, 12:00 PM</b></td><td><b>Preliminary Submission Deadline</b></td><td><b>Hard close — no late submissions or edits accepted</b></td></tr>
  <tr><td>28 Nov 2026</td><td>Finalist Announcement</td><td>Top 10 teams selected + Online Finalist Briefing</td></tr>
  <tr><td>30 Nov 2026</td><td>Online Workshop 2</td><td>Finalist preparation</td></tr>
  <tr><td>4 Dec 2026</td><td>Grand Final &amp; Closing</td><td>Physical at FSKTM, Universiti Malaya, Kuala Lumpur</td></tr>
</table>

<h2>2. Official Rules, Compliance &amp; AI Policy</h2>
<ul>
  <li><b>Primary Data Exclusivity (Rule 2.3):</b> Use <b>only</b> the provided Swift dataset for primary analysis. External primary datasets are strictly prohibited.</li>
  <li><b>External Reference Calibration (Rule 2.4-2.5):</b> Credible public statistics (BIS, IMF, World Bank, SWIFT reports) may be cited to calibrate or explain findings, formatted in <b>APA style with clickable URLs</b>.</li>
  <li><b>Dataset Confidentiality (Rule 2.2):</b> Redistribution, publication, or unauthorized disclosure of the competition dataset (in whole or in part) to third parties is prohibited. <i>Keep any repository holding dataset files strictly private.</i></li>
  <li><b>AI &amp; Tools Policy (Rule 3.5-3.6):</b> Generative AI / LLMs and any analytical tools are explicitly permitted with no separate declaration required, provided the team can fully explain and defend all methods and results.</li>
  <li><b>No Pitch Video Required (Rule 4.3):</b> Preliminary round requires only the Dashboard PDF and Presentation Slide Deck PDF.</li>
</ul>

<h2>3. Submission Deliverables &amp; Judging Rubric</h2>
<table>
  <tr><th>Deliverable</th><th>Format &amp; Length</th><th>Mandatory Requirements</th></tr>
  <tr><td><b>1. Dashboards</b></td><td>PDF (or Looker link + PDF)<br><b>5 to 15 pages</b></td><td>Grouped by feature type (1 feature group per page). Must state the reconstructed business rule(s) clearly and include at least 1 chart per feature group showing baseline comparisons and takeaway titles.</td></tr>
  <tr><td><b>2. Slide Deck</b></td><td>PDF<br><b>10 to 20 slides</b></td><td>Summarize principal insights from dashboards. <b>Max 1 slide per feature group.</b> Must include: Introduction, Methodology, Reconstructed Rules, Supporting Charts, Real-World Economic Explanations, and Rejected Hypotheses.</td></tr>
</table>

<h3>Official Preliminary Round Scoring Weights</h3>
<table>
  <tr><th>Category</th><th>Weight</th><th>Key Sub-Criteria Judges Grade</th></tr>
  <tr><td><b>Insight Quality</b></td><td class="num"><b>45%</b></td><td>Task understanding &amp; testable hypotheses (5%), Rule reconstruction quality (12%), Explanatory depth &amp; causal vs. correlation checks including <b>rejected hypotheses</b> (14%), Specificity with numbers/segments (5%), Correctness vs. reference rules (9%).</td></tr>
  <tr><td><b>Evidence, Method &amp; Integrity</b></td><td class="num"><b>23%</b></td><td>Data integrity, outlier/caveat handling, simple/appropriate reproducible methods, responsible data use &amp; tool disclosure.</td></tr>
  <tr><td><b>Communication</b></td><td class="num"><b>20%</b></td><td>Cohesive narrative structure in slides (6%), standalone clarity of dashboards against baselines (8%), visual clarity with takeaway titles (6%).</td></tr>
  <tr><td><b>Interpretation &amp; Economics</b></td><td class="num"><b>12%</b></td><td>Real-world banking/economic reasoning explaining why the reconstructed rules exist.</td></tr>
</table>

<div class="page-break"></div>

<h2>4. What Is Inside the Dataset? (10,000,000 Rows &bull; 21 Columns &bull; 4.72 GB)</h2>
<p>The dataset (<code>swift_umdac_datathon_2026_fictitious_payment_data.csv</code>) models a directed temporal pseudograph of payment messages between <b>2023-04-30 11:22:26 UTC</b> and <b>2023-07-31 09:56:01 UTC</b> (~92 days), totaling <b>$972,041,020,382.11 USD</b> across <b>155 currencies</b>, <b>8,392 ordering BIC8s</b>, <b>8,266 beneficiary BIC8s</b>, <b>391,132 ordering accounts</b>, and <b>2,590,877 beneficiary accounts</b>.</p>

<div class="warn">
  <b>Data Quality &amp; Cleaning Audit:</b> Structurally, <b>19 of 21 columns have 0 NULLs</b>. However: (1) Embedded newlines inside quoted <code>*_DETAILS</code> expand 10M rows into <b>83,806,705 physical lines</b>—use an RFC-4180 parser (DuckDB/Polars); (2) <code>DISCLAIMER</code> is populated on Row 1 only; (3) <b>1,940 <code>FAT_FINGER_MISTAKE</code> rows</b> (0.019%) inflate total volume by <b>$175.14B (18.02%)</b> and must be isolated before modeling normal values; (4) <code>CUSTOMER_RECALL</code> (317 rows) appears in the CSV despite being omitted from the PDF Appendix.
</div>

<table>
  <tr><th>Column Name</th><th>Type</th><th>Nulls</th><th>Description &amp; Empirical Range</th></tr>
  <tr><td><code>DISCLAIMER</code></td><td>VARCHAR</td><td class="num">9,999,999</td><td>Legal notice on Row 1 only; NULL on all other 9,999,999 rows.</td></tr>
  <tr><td><code>EPOCH_SECONDS</code></td><td>BIGINT</td><td class="num">0</td><td>Unix timestamp (1,682,853,746 to 1,690,797,361).</td></tr>
  <tr><td><code>CURRENCY_CODE</code></td><td>VARCHAR</td><td class="num">0</td><td>155 ISO 4217 currencies; EUR (31.99%) &amp; USD (17.03%) lead.</td></tr>
  <tr><td><code>USD_AMOUNT</code></td><td>DOUBLE</td><td class="num">0</td><td>$0.01 to $15.66B; Median $3,661.90; Mean $97,204.10.</td></tr>
  <tr><td><code>ORDERING_BIC8</code> / <code>BENEFICIARY_BIC8</code></td><td>VARCHAR</td><td class="num">0</td><td>8-char bank IDs; chars 5-6 encode ISO country code (US, CH, GB, FR, DE, SG...).</td></tr>
  <tr><td><code>BIC8_PATH</code></td><td>VARCHAR</td><td class="num">0</td><td>Semicolon-delimited bank route; contains <code>...</code> if discontinuous.</td></tr>
  <tr><td><code>TOTAL_DURATION</code></td><td>BIGINT</td><td class="num">0</td><td>Settlement latency in seconds (2s to 21,649s; Median 56s; Mean 771.5s).</td></tr>
  <tr><td><code>CONTINUITY_QFLAG</code></td><td>VARCHAR</td><td class="num">0</td><td><code>Y</code> = continuous (92.33%); <code>N</code> = gap/hidden bank <code>...</code> (7.67%).</td></tr>
  <tr><td><code>CURRENCY_CONVERSION_COUNT</code></td><td>BIGINT</td><td class="num">0</td><td>FX steps along route (0 to 17; 1 step = 58.96%, 2 steps = 20.18%).</td></tr>
  <tr><td><code>PARTICIPANT_COUNT</code></td><td>BIGINT</td><td class="num">0</td><td>Banks in route (2 to 22; 2 = 63.23%, 3 = 23.24%, 4+ = 13.53%).</td></tr>
  <tr><td><code>TRANSACTION_TYPE_CODE</code></td><td>VARCHAR</td><td class="num">0</td><td><code>Direct</code> (63.23%), <code>Indirect</code> (32.61%), <code>Covered</code> (4.16%).</td></tr>
  <tr><td><code>ORDERING_ACCOUNT</code> / <code>BENEFICIARY_ACCOUNT</code></td><td>VARCHAR</td><td class="num">0</td><td>Anonymized <code>_FAKE_#####</code> IDs (391,132 senders; 2,590,877 receivers).</td></tr>
  <tr><td><code>ORDERING_DETAILS</code> / <code>BENEFICIARY_DETAILS</code></td><td>VARCHAR</td><td class="num">0</td><td>Raw multi-line remittance text (account, name/company, address).</td></tr>
  <tr><td><code>ORDERING_TOKENS</code> / <code>BENEFICIARY_TOKENS</code></td><td>VARCHAR</td><td class="num">0</td><td>19 semantic token families (<code>&lt;chr:&gt;</code>, <code>&lt;street:&gt;</code>, <code>&lt;city:&gt;</code>, <code>&lt;iban:&gt;</code>, etc.).</td></tr>
  <tr><td><code>ORDERING_TYPE</code> / <code>BENEFICIARY_TYPE</code></td><td>VARCHAR</td><td class="num">0</td><td><code>B</code> = Business (78.75% ord / 28.82% ben), <code>C</code> = Consumer (21.25% ord / 71.18% ben).</td></tr>
  <tr><td><code>ANOMALY_TYPE</code></td><td>VARCHAR</td><td class="num">9,992,994</td><td>6 anomaly classes (7,006 rows = 0.0701%); NULL = normal transaction.</td></tr>
</table>

<h2>5. Complete Empirical Breakdown &amp; Categories</h2>
<h3>5.1 Party Flow Categories (ORDERING_TYPE &rarr; BENEFICIARY_TYPE)</h3>
<table>
  <tr><th>Flow</th><th class="num">Count</th><th class="num">Count %</th><th class="num">Median USD</th><th class="num">Mean USD</th><th class="num">Total USD</th><th class="num">Volume %</th></tr>
  {flow_rows}
</table>

<h3>5.2 Top 12 Currencies (of 155) &amp; Geographic Scope</h3>
<table>
  <tr><th class="num">#</th><th>Currency</th><th class="num">Count</th><th class="num">Count %</th><th class="num">Median USD</th><th class="num">Mean USD</th><th class="num">Total USD</th></tr>
  {cur_rows}
</table>
<p><b>Cross-Border vs. Domestic:</b> <b>92.89%</b> (9,288,884 rows) are cross-border (median $3,529, median 55s, avg 1.382 FX) vs. <b>7.11%</b> (711,116 rows) domestic (median $5,669, median 167s, avg 0.830 FX). Same-BIC transfers represent only <b>0.024%</b> (2,387 rows).</p>

<h3>5.3 Anomaly Categories (7,006 Labeled Rows = 0.0701%)</h3>
<table>
  <tr><th>Anomaly Type</th><th class="num">Count</th><th class="num">% of Anom</th><th class="num">Median USD</th><th class="num">Mean USD</th><th class="num">Median Dur</th><th class="num">Cross-Border %</th></tr>
  {anom_rows}
</table>

<div class="page-break"></div>

<h2>6. All 9 Reverse-Engineered Causal Rules &amp; Rejected Hypotheses</h2>
<div class="teal">
  <b>Core Reconstructed Rules (Verified Across All 10,000,000 Rows):</b>
  <ol>
    <li><b>Account Role Permanence (100% Purity):</b> All 391,132/391,132 ordering accounts have an immutable entity type (B or C).</li>
    <li><b>Sender Home-Currency Dominance (83.8%-94.5%):</b> Payments overwhelmingly use the ordering country's home currency (DE 94.5% EUR, FR 94.0% EUR, US 90.5% USD, CH 88.8% CHF, GB 88.6% GBP, JP 88.3% JPY, SG 87.6% SGD), pushing FX downstream.</li>
    <li><b>Local-Timezone Business Hours &amp; Weekend Drop:</b> APAC peaks 00-07 UTC (41-46%), EU peaks 08-15 UTC (41-43%), US peaks 16-23 UTC (46.7%). Weekend volume drops ~75% (Sat 4.35%, Sun 6.84% vs. Mon/Fri 18.34%).</li>
    <li><b>Hop-Count Linear Duration Law (~200s/hop):</b> <code>PARTICIPANT_COUNT</code> drives latency (2 hops: 663s &rarr; 3: 841s &rarr; 4: 1,042s &rarr; 5: 1,242s &rarr; 6: 1,437s &rarr; 7: 1,649s).</li>
    <li><b>Direct-Route Structural Ceiling:</b> <code>Direct</code> (63.23%) strictly enforces 2 participants and FX &isin; {{0, 1}} (0.00% have &ge;2 FX). <code>Indirect</code> &amp; <code>Covered</code> average 3.582 participants and peak at 2 FX (~55.5%).</li>
    <li><b>Flow-Type vs. Routing Independence:</b> Every flow type (B2B, B2C, C2B, C2C) routes identically (~63.2% Direct / ~32.6% Indirect / ~4.1% Covered).</li>
    <li><b>Role-Gated Social Engineering:</b> <code>ROMANCE_SCAM</code> is 100% Consumer-originated (500 senders &rarr; 378 mules, median $109.45, median 1,148s). <code>CEO_SCAM</code> is 100% Business-originated (98.73% cross-border, median $20,602).</li>
    <li><b>Error &amp; Replay Mechanics:</b> <code>FAT_FINGER_MISTAKE</code> inflates median amount 71x ($260,241; $175.14B total = 18.02% of dataset volume) with normal duration (53s). <code>DUPLICATE_PAYMENT</code> replays 185 exact tuples within 0-6,940s (median 1,099s).</li>
    <li><b>Discontinuity &amp; Recall Coupling:</b> Undocumented <code>CUSTOMER_RECALL</code> (317 rows) has the highest path discontinuity rate (11.04% <code>CONTINUITY_QFLAG='N'</code> vs. 7.67% normal).</li>
  </ol>
</div>

<div class="callout">
  <b>Rejected Hypotheses (Include in Slide Deck for Rubric 1.3):</b><br>
  &bull; <i>Rejected #1:</i> "High-value B2B wires use Covered/Indirect routing more than C2C." &rarr; <b>Disproved:</b> Direct share is 63.22% (B2B), 63.23% (B2C), 63.19% (C2B), 63.28% (C2C).<br>
  &bull; <i>Rejected #2:</i> "More FX conversions drive longer settlement duration." &rarr; <b>Disproved:</b> Controlling for 4 participants, median duration is 429s (0 FX), 418s (1 FX), 418s (2 FX), 418s (3 FX). Hop count, not FX count, drives latency.
</div>

<h2>7. 3-Person Action Plan &amp; Pre-Submission Checklist</h2>
<table>
  <tr><th>Team Role</th><th>Owned Deliverables &amp; Rubric Focus</th><th>Concrete Tasks Before 19 Nov 12:00 PM</th></tr>
  <tr><td><b>Person 1: Data &amp; Causal Lead</b></td><td>Methodology, Rejected Hypotheses, Compliance (Rubric 1.3, 2.x, 3.x)</td><td>Verify all metrics in <code>data/pass1-4.json</code>, document RFC-4180 parsing &amp; fat-finger isolation, finalize rejected hypotheses and tool disclosure.</td></tr>
  <tr><td><b>Person 2: Dashboard Lead</b></td><td>Deliverable 1: 8-Page Dashboard PDF (Rubric 4.2, 4.3)</td><td>Review <code>Swift_UMDAC_Datathon_2026_Dashboards.pdf</code> (8 pages, within 5-15 limit), verify takeaway titles &amp; baselines on every chart.</td></tr>
  <tr><td><b>Person 3: Storytelling &amp; Slides Lead</b></td><td>Deliverable 2: 10-20 Slide Deck PDF (Rubric 4.1, Econ 12%)</td><td>Build 14-16 slide deck (max 1 slide/feature group) pairing charts, causal rules, real-world banking logic, and APA external citations if used.</td></tr>
</table>

<h3>Final Pre-Submission QA Checklist</h3>
<ul>
  <li>[ ] <b>Dashboard PDF:</b> 5-15 pages, 1 feature group per page, explicit rule statements + charts (<code>Swift_UMDAC_Datathon_2026_Dashboards.pdf</code> = 8 pages, ready).</li>
  <li>[ ] <b>Slide Deck PDF:</b> 10-20 slides total, max 1 slide per feature group, includes Intro, Methodology, Rules, Economic Logic, Rejected Hypotheses, and Tool Disclosure.</li>
  <li>[ ] <b>Cross-Check &amp; Upload:</b> All numbers match across both PDFs; submit via official Datathon portal before <b>19 November 2026, 12:00 PM (UTC+8)</b>.</li>
</ul>

</body>
</html>
"""

with open(OUT_HTML, "w") as f:
    f.write(html_doc)
print("Wrote Master Guide HTML:", OUT_HTML)
