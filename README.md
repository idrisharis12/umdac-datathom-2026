# UMDAC Datathon 2026 – Swift Cross-Border Payments Analytics

Official repository for the **Universiti Malaya Data Analytics Club (UMDAC) Datathon 2026** Preliminary Round challenge in collaboration with **SWIFT**.

---

## 📋 Table of Contents
1. [Competition Overview & Timeline](#competition-overview--timeline)
2. [The Challenge: Reverse-Engineering Swift's Synthetic Payment Engine](#the-challenge-reverse-engineering-swifts-synthetic-payment-engine)
3. [Dataset Architecture & Comprehensive Feature Dictionary](#dataset-architecture--comprehensive-feature-dictionary)
4. [Empirical Dataset Statistics & Anomaly Profiles](#empirical-dataset-statistics--anomaly-profiles)
5. [Dataset Packaging & Reassembly Guide](#dataset-packaging--reassembly-guide)
6. [Preliminary Round Submission Deliverables](#preliminary-round-submission-deliverables)
7. [Official Evaluation Rubric & Scoring Weights](#official-evaluation-rubric--scoring-weights)
8. [Reverse-Engineering Framework & Feature-Group Blueprints](#reverse-engineering-framework--feature-group-blueprints)
9. [High-Performance Data Processing Guide](#high-performance-data-processing-guide)
10. [Rules, Academic Integrity & Compliance](#rules-academic-integrity--compliance)
11. [Full-Dataset Analysis Deliverables & Reverse-Engineered Causal Rules](#11-full-dataset-analysis-deliverables--reverse-engineered-causal-rules)

---

## 1. Competition Overview & Timeline

The **UMDAC Datathon 2026** is an international data analytics competition organised by the Universiti Malaya Data Analytics Club (UMDAC) in collaboration with SWIFT. The competition tests participants' ability to uncover underlying causal data generation mechanisms, reverse-engineer synthetic economic dynamics, and formulate actionable financial intelligence.

### Critical Deadlines & Milestones
* **Preliminary Round Commencement**: 13 November 2026 at 11:50 AM (UTC+8)
* **Preliminary Round Submission Deadline**: **19 November 2026 at 12:00 PM (UTC+8)** (Strict 144-hour sprint)
* **Online Workshop 1 (Data Science & Analytics)**: 17 November 2026 (Tuesday)
* **Finalist Announcement**: 28 November 2026 (Saturday)
* **Online Workshop 2 (Finalist Preparation)**: 30 November 2026 (Monday)
* **Physical Grand Final & Closing Ceremony**: 4 December 2026 (Friday) at the Faculty of Computer Science & Information Technology (FSKTM), Universiti Malaya, Kuala Lumpur.

---

## 2. The Challenge: Reverse-Engineering Swift's Synthetic Payment Engine

### The Context
Swift interconnects over 11,500 financial institutions, market infrastructures, fintechs, and corporate enterprises across 200+ countries and territories. Cross-border payments traversing the Swift network represent a **directed temporal pseudograph** where institutions (BICs) and customer accounts form vertices, and payment messages (MT103 / pacs.008) form directed edges with inter-dependent transactional features.

Due to global banking secrecy and data privacy mandates (GDPR), Swift distilled real-world payment traffic dynamics into a synthetic data generator written in Python using hard-coded business logic, the `Faker` library, and NumPy random distribution models.

### The Problem Statement
Participants must **reverse-engineer the underlying generating rules and causal logic** used to construct the dataset.

> **Key Rule Requirement**:
> Findings must be framed as explicit, testable causal rules rather than simple correlations:
> $$\text{Rule Structure: When [Condition } X\text{], [Target Feature } Y\text{] changes by [Factor } Z\text{] across [Segment } W\text{].}$$

*Note on Synthetic Boundaries*: Baseline properties (e.g., country populations, city geography, and Faker-generated entity names) are randomized for public release. The underlying **economic decision rules, routing behavior, clearing latency cut-offs, and anomaly injection mechanisms** follow strict causal logic.

---

## 3. Dataset Architecture & Comprehensive Feature Dictionary

The primary data file is `swift_umdac_datathon_2026_fictitious_payment_data.csv`:
* **Exact Total Records**: **10,000,000 payment instructions**
* **Total Physical CSV Lines**: 83,806,705 lines (due to embedded multiline formatting in party details and token strings)
* **Raw File Size**: 4,952,194,328 bytes (~4.95 GB)
* **Compressed ZIP Size**: 1,563,561,489 bytes (~1.56 GB)

### The 21 Features

| # | Column Name | Data Type | Description & Reverse-Engineering Relevance |
| :---: | :--- | :--- | :--- |
| 1 | `DISCLAIMER` | Text | Legal header / metadata disclaiming liability for fictitious data. |
| 2 | `EPOCH_SECONDS` | Integer | Unix timestamp in seconds. Used to analyze diurnal rhythms, business hours, weekend effects, and clearing cut-offs. |
| 3 | `CURRENCY_CODE` | Categorical | ISO 4217 code (EUR, USD, GBP, CHF, SGD, TRY, CNY, JPY, AUD, CAD, etc.). |
| 4 | `USD_AMOUNT` | Float | Transaction amount normalized to USD for cross-currency equivalence. |
| 5 | `ORDERING_BIC8` | String (8 char) | Sending institution BIC (4 bank + 2 country + 2 location). |
| 6 | `BENEFICIARY_BIC8` | String (8 char) | Receiving institution BIC. |
| 7 | `BIC8_PATH` | String | Semicolon-delimited chain of intermediary routing institutions (e.g., `0024TRI0;0380CNB0`). Gaps marked by `...`. |
| 8 | `TOTAL_DURATION` | Integer | Total elapsed payment settlement time in seconds from initiation to completion. |
| 9 | `CONTINUITY_QFLAG` | Binary (`Y`/`N`) | `Y` if full intermediary path is observable; `N` if route contains hidden intermediaries (`...`). |
| 10 | `CURRENCY_CONVERSION_COUNT` | Integer | Number of FX conversion steps along the routing path (0 = single-currency, $\ge 1$ = FX required). |
| 11 | `PARTICIPANT_COUNT` | Integer | Total number of financial institutions in the settlement path. |
| 12 | `TRANSACTION_TYPE_CODE` | Categorical | Routing mechanism: `Direct` (bilateral), `Indirect` (intermediaries), or `Covered` (MT202COV bank-to-bank settlement). |
| 13 | `ORDERING_ACCOUNT` | String | Anonymized synthetic account ID for the sender (`_FAKE_...`). |
| 14 | `BENEFICIARY_ACCOUNT` | String | Anonymized synthetic account ID for the recipient (`_FAKE_...`). |
| 15 | `ORDERING_DETAILS` | Free-text | Semi-structured remittance party information (name, address, postal code, country code, line breaks). |
| 16 | `ORDERING_TOKENS` | Tokenized Text | Engineered semantic pattern tokens (e.g., `<business:7>`, `<street:18>`, `<post_code:US:5>`, `<line_break:35>`). |
| 17 | `BENEFICIARY_DETAILS` | Free-text | Semi-structured recipient party details and remittance instructions. |
| 18 | `BENEFICIARY_TOKENS` | Tokenized Text | Engineered pattern tokens for beneficiary entity attributes. |
| 19 | `ORDERING_TYPE` | Categorical (`B`/`C`) | Sender classification: `B` (Corporate / Business) vs. `C` (Retail / Consumer). |
| 20 | `BENEFICIARY_TYPE` | Categorical (`B`/`C`) | Recipient classification: `B` (Corporate / Business) vs. `C` (Retail / Consumer). |
| 21 | `ANOMALY_TYPE` | Categorical (Label) | Ground-truth injection flag indicating synthetic fraud or operational errors. |

---

## 4. Empirical Dataset Statistics & Anomaly Profiles

Empirical profiling across the 10,000,000 records reveals key baseline properties and distinct anomaly footprints:

### Traffic Distributions
* **Transaction Types**: Direct (~63.2%), Indirect (~32.6%), Covered (~4.2%).
* **Ordering Entity Types**: Business `B` (~78.7%), Consumer `C` (~21.3%).
* **Beneficiary Entity Types**: Consumer `C` (~71.1%), Business `B` (~28.9%).
* **Top Settlement Currencies**: EUR (~32.1%), USD (~17.2%), GBP (~8.8%), CHF (~7.9%), SGD (~3.7%), CNY (~3.3%).
* **Route Continuity**: Observable `Y` (~92.4%), Obfuscated / Gap `N` (~7.6%).

### Ground-Truth Anomaly Profiles (`ANOMALY_TYPE`)

```mermaid
graph TD
    Pop["10,000,000 Transactions"] --> Legitimate["Legitimate Traffic (~99.86%)"]
    Pop --> Injected["Injected Anomalies (~0.14%)"]
    Injected --> RS["ROMANCE_SCAM (100% C -> C/B, Mean: $4.3K USD)"]
    Injected --> CS["CEO_SCAM (100% B -> C, Mean: $2.2M USD, Max: $17M)"]
    Injected --> FF["FAT_FINGER_MISTAKE (Shifted decimal, Outliers up to $3.35B)"]
    Injected --> ARS["ACCOUNT_REPLACEMENT_SCAM (Hijacked vendor accounts)"]
    Injected --> DP["DUPLICATE_PAYMENT (Exact duplicate (Amount, Parties) at Δt ≈ 0)"]
    Injected --> CR["CUSTOMER_RECALL (Out-of-band recall / stop-payment requests)"]
```

| Anomaly Type | Sender Archetype | Recipient Archetype | Routing Distribution | Sizing & Behavioral Signature |
| :--- | :---: | :---: | :--- | :--- |
| **`ROMANCE_SCAM`** | **100% `C`** | 77% `C`, 23% `B` | 54% Direct, 46% Indirect | Modest retail outflows (mean: \$4,351 USD; median: \$800–\$2,500). Recurring cross-border gifts/support. |
| **`CEO_SCAM`** | **100% `B`** | 88% `C`, 12% `B` | 56% Direct, 44% Indirect | Extreme values (mean: \$2,214,148 USD, up to \$16.9M USD). Spoofed executive instructions paying individual mule accounts. |
| **`FAT_FINGER_MISTAKE`** | 80% `B`, 20% `C` | 71% `C`, 29% `B` | 54% Direct, 32% Indirect, 14% Covered | Comma/period placement error multiplying amounts by $10^2$ to $10^3$ (mean: \$124.6M USD, max: **\$3.35 Billion USD**). |
| **`ACCOUNT_REPLACEMENT_SCAM`** | 56% `B`, 44% `C` | 56% `C`, 44% `B` | 81% Direct, 19% Indirect | Legitimate invoice intercepted; beneficiary account swapped to an unverified recipient (mean: \$146K USD). |
| **`DUPLICATE_PAYMENT`** | **100% `B`** | **100% `C`** | 100% Indirect | Exact duplicate tuples `(ORDERING_ACCOUNT, BENEFICIARY_ACCOUNT, USD_AMOUNT)` executed within seconds (race condition). |
| **`CUSTOMER_RECALL`** | **100% `B`** | 50% `B`, 50% `C` | 75% Direct, 25% Covered | Formal recall message following erroneous payment instruction. |

---

## 5. Dataset Packaging & Reassembly Guide

Due to GitHub's strict file size limit (maximum 2.00 GB per object in Git LFS), the 4.95 GB CSV is stored using two redundant, validated methods:

### Option A: Unzip the Archive (Recommended)
```bash
unzip swift_umdac_datathon_2026_fictitious_payment_data.zip
```

### Option B: Reassemble Multi-Part LFS Chunks
The CSV is partitioned into three chunks strictly under 1.7 GB:
* `swift_umdac_datathon_2026_fictitious_payment_data.csv.part_aa` (1.7 GB)
* `swift_umdac_datathon_2026_fictitious_payment_data.csv.part_ab` (1.7 GB)
* `swift_umdac_datathon_2026_fictitious_payment_data.csv.part_ac` (1.4 GB)

To reassemble the original 4.95 GB file with a single command:
```bash
chmod +x reassemble_csv.sh
./reassemble_csv.sh
```
Or directly via shell:
```bash
cat swift_umdac_datathon_2026_fictitious_payment_data.csv.part_* > swift_umdac_datathon_2026_fictitious_payment_data.csv
```

---

## 6. Preliminary Round Submission Deliverables

Participating teams must submit **two PDF deliverables** before **19 November 2026 at 12:00 PM**:

### Deliverable 1: Dashboard Suite (PDF Format)
* **Volume**: 5 to 15 dashboard pages (one page per feature group).
* **Format**: Exported from Looker Studio, Tableau, Power BI, or equivalent.
* **Requirements per Page**:
  * Clear header stating the reconstructed business rule.
  * At least one primary chart illustrating how the rule manifests in data.
  * Baseline / control group comparison.
* **Grading Criteria**: Effectiveness of Charts & Evidence (50%), Visual Clarity (35%), Correctness of Insights (15%).

### Deliverable 2: Presentation Slide Deck (PDF Format)
* **Volume**: 10 to 20 slides total.
* **Constraint**: **Maximum of 1 slide per feature-type group**.
* **Required Slide Structure**:
  1. Title & Team Overview
  2. Executive Summary (Headline Findings)
  3. Reverse-Engineering Methodology & Hypothesis Testing Framework
  4–11. Feature-Group Deep Dives (Rule statement, Dashboard chart, Real-world economic rationale, Counterfactual controls)
  12. Multi-Factor Causal Interaction Model
  13. Anomaly Detection Decision Matrix
  14. **Tested & Rejected Hypotheses** (critical for explanatory depth score)
  15. Synthetic Boundaries vs. Real-World Banking Dynamics
  16. Conclusion & Recommendations
* **Grading Criteria**: Methodology & Analytical Process (65%), Economic Explanations (20%), Overall Presentation Quality (15%).

---

## 7. Official Evaluation Rubric & Scoring Weights

Across both deliverables, marks are allocated across four core pillars:

```mermaid
pie title Official Preliminary Round Scoring
    "Insight Quality" : 45
    "Evidence, Method & Data Integrity" : 23
    "Communication" : 20
    "Interpretation & Economic Reasoning" : 12
```

### Detailed Sub-Criteria
1. **Insight Quality (45%)**:
   * *Rule Reconstruction Quality (12%)*: Stating exact preconditions, magnitude of change, and segment coverage.
   * *Explanatory Depth (14%)*: Distinguishing causality from correlation; rigorously evaluating confounding factors; reporting rejected hypotheses.
   * *Correctness of Rules (9%)*: Accuracy of recovered rules against Swift's true generator script.
   * *Task Understanding (5%)* & *Specificity (5%)*: Quantified, single-sentence headline claims.
2. **Evidence, Method & Data Integrity (23%)**:
   * *Method Appropriateness (8%)*: Using defensible, interpretable techniques (decision trees, regression, counterfactuals). Unnecessary black-box complexity is penalized.
   * *Empirical Proof (6%)* & *Data Integrity (6%)*: Honest axes, confidence intervals, correct Unix timestamp conversion to UTC/local hours.
   * *Responsible Data Use (3%)*: Strict adherence to provided data; APA citations for external reference statistics.
3. **Communication (20%)**:
   * *Dashboard Quality (8%)*: Self-explanatory views with clear baselines and callouts.
   * *Narrative Structure (6%)*: Headline-led progression in slides.
   * *Visual Clarity (6%)*: Zero clutter; single takeaway per visual.
4. **Interpretation & Economic Reasoning (12%)**:
   * *Plausibility (6%)*: Grounding findings in correspondent banking, Nostro/Vostro liquidity, and RTGS clearing cut-offs.
   * *Scope & Limits (6%)*: Distinguishing synthetic artifacts from economic rules.

---

## 8. Reverse-Engineering Framework & Feature-Group Blueprints

To fulfill the 5–15 dashboard and slide requirements, analyze these 8 distinct feature groups:

1. **Feature Group 1: Transaction Sizing & Benford's Law (`USD_AMOUNT`)**
   * *Rule*: Legitimate amounts follow log-normal distributions segmented by entity pair ($B \to B \gg B \to C \gg C \to C$).
   * *Anomaly*: `FAT_FINGER_MISTAKE` multiplies intended amounts by $10^2$ or $10^3$, creating observable decimal transposition spikes.
2. **Feature Group 2: Temporal Clearing & Diurnal Dynamics (`EPOCH_SECONDS`, `TOTAL_DURATION`)**
   * *Rule*: Payment duration $T$ is a step function of local business hours. Payments submitted after 17:00 local time or on weekends exhibit a duration spike equal to the time delta until 08:00 of the next business day.
3. **Feature Group 3: Routing Selection Mechanics (`TRANSACTION_TYPE_CODE`, `BIC8_PATH`)**
   * *Rule*: Direct routing requires bilateral correspondent accounts. When currency conversion is required or jurisdictions lack direct settlement rails, the generator switches to `Indirect` or `Covered` routing.
4. **Feature Group 4: Foreign Exchange Dynamics (`CURRENCY_CODE`, `CURRENCY_CONVERSION_COUNT`)**
   * *Rule*: Cross-border payments where ordering and beneficiary countries share a regional currency (e.g., EUR within SEPA) maintain conversion count $= 0$. Inter-continental payments invoke $1$ or $2$ FX hops through global reserve hubs (USD, EUR).
5. **Feature Group 5: Counterparty Interaction Matrices (`ORDERING_TYPE`, `BENEFICIARY_TYPE`)**
   * *Rule*: Transaction volume is dominated by $B \to C$ payroll/dividends and $B \to B$ commercial trade. $C \to C$ is heavily localized or remittance-specific.
6. **Feature Group 6: Semantic Token Syntax (`ORDERING_TOKENS`, `BENEFICIARY_TOKENS`)**
   * *Rule*: The generator builds details using regex token rules (`<iban>`, `<street>`, `<business>`, `<line_break:35>`). Anomalies often contain malformed or missing address tokens.
7. **Feature Group 7: Path Obfuscation & Dark Routing (`CONTINUITY_QFLAG`)**
   * *Rule*: `CONTINUITY_QFLAG = N` triggers when payments route through non-cooperative jurisdictions, multi-tier correspondent chains, or covered serial legs where intermediary visibility is masked (`...`).
8. **Feature Group 8: Financial Crime Decision Boundaries (`ANOMALY_TYPE`)**
   * *Rule*: CEO Scams require $B \to C$ routing with values exceeding \$500,000 USD; Romance Scams require $C \to C$ retail payments with recurring temporal clusters.

---

## 9. High-Performance Data Processing Guide

Because the dataset is 4.95 GB with 10,000,000 records, standard `pandas.read_csv()` will exhaust RAM. Use **Polars** (lazy scanning) or **DuckDB**:

```python
import polars as pl

# 1. Connect via LazyFrame (Zero RAM overhead)
lazy_df = pl.scan_csv("swift_umdac_datathon_2026_fictitious_payment_data.csv")

# 2. Extract anomaly breakdown across transaction and entity types
anomaly_summary = (
    lazy_df
    .filter(pl.col("ANOMALY_TYPE") != "")
    .group_by(["ANOMALY_TYPE", "ORDERING_TYPE", "BENEFICIARY_TYPE", "TRANSACTION_TYPE_CODE"])
    .agg([
        pl.count().alias("count"),
        pl.col("USD_AMOUNT").mean().alias("mean_usd"),
        pl.col("USD_AMOUNT").median().alias("median_usd"),
        pl.col("TOTAL_DURATION").mean().alias("mean_duration_sec")
    ])
    .sort("count", descending=True)
    .collect()
)

print(anomaly_summary)
```

---

## 10. Rules, Academic Integrity & Compliance

* **Exclusivity of Primary Data**: Only the provided Swift dataset may be used for primary empirical modeling. External primary datasets are strictly banned.
* **External Reference Calibration**: Public reference statistics (World Bank, BIS, IMF, SWIFT reports) are permitted solely to contextualize and calibrate findings, and must be cited in **APA format** with clickable URLs.
* **AI Tool Allowance**: Generative AI tools (ChatGPT, Claude, Gemini, Copilot) are explicitly permitted for coding, analysis, and slide design. No declaration is required, but teams must be able to explain, defend, and justify all methods during judging.

---

## 11. Full-Dataset Analysis Deliverables & Reverse-Engineered Causal Rules

Exact full-table SQL profiling across all **10,000,000 rows** (using DuckDB 2.0.0) has been completed and packaged into this repository:

### Repository Additions
* **Word Report:** [`Swift_UMDAC_Datathon_2026_Data_Analysis_Report.docx`](Swift_UMDAC_Datathon_2026_Data_Analysis_Report.docx) — 12-page technical report covering schema completeness, party-flow & currency categories, routing/FX architecture, temporal patterns, token taxonomy, anomaly forensics, and all 9 reconstructed generating rules.
* **Aggregated Summary Data (`data/`):** `pass1_summary.json`, `pass2_summary.json`, `pass3_summary.json`, `pass4_causal_rules.json` (exact 10M-row counts, quantiles, cross-tabs, and causal tests).
* **Visualizations (`charts/`):** `chart1_flow_types.png` through `chart6_anomalies.png`.
* **Reproducible Scripts (`scripts/`):** `analyze_pass1.py`–`analyze_pass4.py`, `make_charts.py`, and `generate_report.js`.

### 9 Reverse-Engineered Generating Rules & Causal Logic

| # | Reconstructed Rule | Empirical Proof (10,000,000 Rows) | Economic / System Logic |
| :-: | :--- | :--- | :--- |
| **1** | **Account Role Permanence** | **391,132 / 391,132 (100.00%)** `ORDERING_ACCOUNT`s have a single immutable `ORDERING_TYPE` (`B` or `C`). | Entity type is a fixed node property in the payment graph, never resampled per edge. |
| **2** | **Sender Home-Currency Dominance** | **83.8%–94.5%** of wires use the ordering country's home currency (`DE` 94.5% EUR, `FR` 94.0% EUR, `US` 90.5% USD, `CH` 88.8% CHF, `GB` 88.6% GBP, `JP` 88.3% JPY, `SG` 87.6% SGD). | Exporters and corporates initiate payments in their domestic operating currency, pushing FX conversion downstream. |
| **3** | **Local-Timezone Business-Hour Modulation** | Asia-Pacific (`AU` 46.4%, `JP` 41.9%, `CN` 41.5%, `SG` 40.7%) peaks `00:00–07:59 UTC`; Europe (`DE` 43.0%, `CH` 42.7%, `GB` 41.3%) peaks `08:00–15:59 UTC`; `US` (46.7%) peaks `16:00–23:59 UTC`. Weekend volume drops ~75% (Sat 4.35%, Sun 6.84% vs. Mon/Fri 18.34%). | Payment initiation follows local banking hours and RTGS/clearing calendar closures. |
| **4** | **Hop-Count Linear Duration Law** | `PARTICIPANT_COUNT` (not FX count) drives latency by **~200s per hop**: mean duration scales `663s (2) -> 841s (3) -> 1,042s (4) -> 1,242s (5) -> 1,437s (6) -> 1,649s (7)`. | Each correspondent intermediary adds a clearing/compliance hop delay. |
| **5** | **Direct-Route Structural Ceiling** | `Direct` (63.23%) strictly enforces `PARTICIPANT_COUNT = 2` and `CURRENCY_CONVERSION_COUNT ∈ {0, 1}` (**0.00%** have $\ge 2$ FX steps). `Indirect` (32.61%) & `Covered` (4.16%) average `3.582` participants and peak at `2` FX steps (~55.5%). | Bilateral Nostro/Vostro links settle in 2 hops with at most one FX leg; correspondent chains require multi-hop FX. |
| **6** | **Flow-Type vs. Routing Independence** | Every flow category (`B2B`, `B2C`, `C2B`, `C2C`) routes at **~63.2% Direct / ~32.6% Indirect / ~4.1% Covered**, despite `B2B` median value ($22,888) being ~50× `C2C` ($463). | Routing topology is determined by bank-corridor relationships rather than customer ticket size. |
| **7** | **Role-Gated Social Engineering** | `ROMANCE_SCAM` (2,476 rows) is **100% Consumer-originated** (`C2C` 73.1%, `C2B` 26.9%) across just **500 senders & 378 receivers** (median $109.45, median 1,148s). `CEO_SCAM` (945 rows) is **100% Business-originated** (`B2C` 72.3%, `B2B` 27.7%, median $20,602). | Fraud injection enforces realistic victim-type constraints and mule-account reuse. |
| **8** | **Error & Replay Mechanics** | `FAT_FINGER_MISTAKE` (1,940 rows) keeps normal duration (median 53s) but inflates median amount **71×** ($260,241; **$175.14B** total = **18.02%** of all dataset volume). `DUPLICATE_PAYMENT` (679 rows) replays **185** exact `(sender, receiver, amount)` tuples within `0–6,940s` (median `1,099s`). | Models human decimal-entry errors and back-office race-condition retries. |
| **9** | **Discontinuity & Recall Coupling** | `CUSTOMER_RECALL` (317 rows, undocumented in PDF Appendix) has the highest path discontinuity rate (**11.04%** `CONTINUITY_QFLAG = 'N'` vs. 7.67% normal). | Recalls disproportionately surface along opaque/incomplete correspondent chains. |

---
*Maintained for UMDAC Datathon 2026.*
