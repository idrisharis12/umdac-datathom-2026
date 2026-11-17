const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak, LevelFormat, ImageRun, TableOfContents
} = require("docx");

const SCRATCH = "/home/blakie/.gemini/antigravity-cli/brain/9207bfc3-2551-4cda-ad91-4687664bef3f/scratch";
const CHART_DIR = path.join(SCRATCH, "charts");
const OUT_DOCX = "/home/blakie/Work/Swift_UMDAC_Datathon_2026_Data_Analysis_Report.docx";

const readJson = (f) => JSON.parse(fs.readFileSync(path.join(SCRATCH, f), "utf8").replace(/\bNaN\b/g, "null"));
const p1 = readJson("pass1_summary.json");
const p2 = readJson("pass2_summary.json");
const p3 = readJson("pass3_summary.json");

const NAVY = "1B365D";
const TEAL = "006D77";
const CORAL = "C84B31";
const LIGHT_BG = "F2F5F9";
const ALT_ROW = "F8FAFC";
const BORDER_HEX = "D0D7DE";
const TEXT_DARK = "1F2937";
const TEXT_MUTED = "4B5563";

const CONTENT_WIDTH = 9360; // 12240 - 2*1440

const cellBorders = {
  top: { style: BorderStyle.SINGLE, size: 4, color: BORDER_HEX },
  bottom: { style: BorderStyle.SINGLE, size: 4, color: BORDER_HEX },
  left: { style: BorderStyle.SINGLE, size: 4, color: BORDER_HEX },
  right: { style: BorderStyle.SINGLE, size: 4, color: BORDER_HEX },
};

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 320, after: 140 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: NAVY, space: 4 } },
    children: [new TextRun({ text, bold: true, size: 30, color: NAVY, font: "Calibri" })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 100 },
    children: [new TextRun({ text, bold: true, size: 24, color: TEAL, font: "Calibri" })],
  });
}

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.after ?? 120, line: 276 },
    alignment: opts.align ?? AlignmentType.LEFT,
    children: [
      new TextRun({
        text,
        size: opts.size ?? 21,
        bold: opts.bold ?? false,
        italics: opts.italics ?? false,
        color: opts.color ?? TEXT_DARK,
        font: "Calibri",
      }),
    ],
  });
}

function pRich(runs, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.after ?? 120, line: 276 },
    children: runs.map(
      (r) =>
        new TextRun({
          text: r.text,
          bold: r.bold ?? false,
          italics: r.italics ?? false,
          size: r.size ?? 21,
          color: r.color ?? TEXT_DARK,
          font: r.font ?? "Calibri",
        })
    ),
  });
}

function bullet(boldPrefix, restText) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 80, line: 264 },
    children: [
      new TextRun({ text: boldPrefix, bold: true, size: 21, color: TEXT_DARK, font: "Calibri" }),
      new TextRun({ text: restText, size: 21, color: TEXT_DARK, font: "Calibri" }),
    ],
  });
}

function callout(title, body) {
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [CONTENT_WIDTH],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: CONTENT_WIDTH, type: WidthType.DXA },
            shading: { fill: LIGHT_BG, type: ShadingType.CLEAR },
            borders: {
              top: { style: BorderStyle.SINGLE, size: 4, color: BORDER_HEX },
              bottom: { style: BorderStyle.SINGLE, size: 4, color: BORDER_HEX },
              right: { style: BorderStyle.SINGLE, size: 4, color: BORDER_HEX },
              left: { style: BorderStyle.SINGLE, size: 24, color: NAVY },
            },
            margins: { top: 120, bottom: 120, left: 180, right: 160 },
            children: [
              new Paragraph({
                spacing: { after: 60 },
                children: [new TextRun({ text: title, bold: true, size: 21, color: NAVY, font: "Calibri" })],
              }),
              new Paragraph({
                spacing: { after: 0, line: 260 },
                children: [new TextRun({ text: body, size: 20, color: TEXT_DARK, font: "Calibri" })],
              }),
            ],
          }),
        ],
      }),
    ],
  });
}

function makeTable(headers, rows, colWidths, rightAlignCols = new Set()) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) =>
      new TableCell({
        width: { size: colWidths[i], type: WidthType.DXA },
        shading: { fill: NAVY, type: ShadingType.CLEAR },
        borders: cellBorders,
        margins: { top: 90, bottom: 90, left: 110, right: 110 },
        children: [
          new Paragraph({
            alignment: rightAlignCols.has(i) ? AlignmentType.RIGHT : AlignmentType.LEFT,
            children: [new TextRun({ text: h, bold: true, size: 19, color: "FFFFFF", font: "Calibri" })],
          }),
        ],
      })
    ),
  });

  const dataRows = rows.map((row, rIdx) =>
    new TableRow({
      children: row.map((val, cIdx) =>
        new TableCell({
          width: { size: colWidths[cIdx], type: WidthType.DXA },
          shading: { fill: rIdx % 2 === 1 ? ALT_ROW : "FFFFFF", type: ShadingType.CLEAR },
          borders: cellBorders,
          margins: { top: 75, bottom: 75, left: 110, right: 110 },
          children: [
            new Paragraph({
              alignment: rightAlignCols.has(cIdx) ? AlignmentType.RIGHT : AlignmentType.LEFT,
              children: [new TextRun({ text: String(val), size: 19, color: TEXT_DARK, font: "Calibri" })],
            }),
          ],
        })
      ),
    })
  );

  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows],
  });
}

function addChart(filename, caption, widthPx = 560, heightPx = 240) {
  const imgData = fs.readFileSync(path.join(CHART_DIR, filename));
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 140, after: 60 },
      children: [
        new ImageRun({
          type: "png",
          data: imgData,
          transformation: { width: widthPx, height: heightPx },
        }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 160 },
      children: [new TextRun({ text: caption, italics: true, size: 18, color: TEXT_MUTED, font: "Calibri" })],
    }),
  ];
}

const fmtInt = (n) => Number(n).toLocaleString("en-US");
const fmtUsd = (n) => "$" + Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtB = (n) => "$" + (Number(n) / 1e9).toFixed(2) + "B";

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "\u2022",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 480, hanging: 240 } } },
          },
        ],
      },
    ],
  },
  styles: {
    default: {
      document: {
        run: { font: "Calibri", size: 21, color: TEXT_DARK },
      },
    },
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              alignment: AlignmentType.RIGHT,
              children: [
                new TextRun({
                  text: "UMDAC Datathon 2026 | Swift Fictitious Payment Dataset Analysis",
                  size: 17,
                  color: TEXT_MUTED,
                  font: "Calibri",
                }),
              ],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({ text: "Page ", size: 17, color: TEXT_MUTED, font: "Calibri" }),
                new TextRun({ children: [PageNumber.CURRENT], size: 17, color: TEXT_MUTED, font: "Calibri" }),
                new TextRun({ text: " of ", size: 17, color: TEXT_MUTED, font: "Calibri" }),
                new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 17, color: TEXT_MUTED, font: "Calibri" }),
              ],
            }),
          ],
        }),
      },
      children: [
        // COVER / TITLE BLOCK
        new Paragraph({ spacing: { before: 720, after: 120 }, children: [
          new TextRun({ text: "TECHNICAL DATA ANALYSIS REPORT", bold: true, size: 22, color: TEAL, font: "Calibri" }),
        ]}),
        new Paragraph({ spacing: { after: 180 }, children: [
          new TextRun({ text: "Swift UMDAC Datathon 2026: Fictitious Payment Dataset", bold: true, size: 44, color: NAVY, font: "Calibri" }),
        ]}),
        p("Comprehensive Full-Scan Profiling, Category Taxonomy, Causal Rule Discovery, and Anomaly Forensics across 10,000,000 Synthetic Cross-Border & Domestic Payment Records", { size: 24, color: TEXT_MUTED, after: 300 }),
        makeTable(
          ["Dataset Attribute", "Observed Value"],
          [
            ["Source File", "swift_umdac_datathon_2026_fictitious_payment_data.csv (4,722.8 MB / 4.72 GB)"],
            ["Total Payment Records", "10,000,000 rows (83,806,705 physical lines due to embedded newlines)"],
            ["Schema Width", "21 columns (Timestamp, Currency, Amount, BIC8 Routing, Accounts, Details, Tokens, Types, Anomalies)"],
            ["Observation Window", "2023-04-30 11:22:26 UTC to 2023-07-31 09:56:01 UTC (~92 days, Q2-Q3 2023)"],
            ["Aggregate Volume", "$972,041,020,382.11 USD (~$972.04 Billion)"],
            ["Distinct Currencies & BICs", "155 ISO 4217 currencies; 8,392 ordering BIC8s; 8,266 beneficiary BIC8s"],
            ["Distinct Accounts", "391,132 ordering accounts; 2,590,877 beneficiary accounts"],
            ["Labeled Anomalies", "7,006 records (0.0701%) across 6 distinct categories (9,992,994 normal / NULL)"],
          ],
          [2800, 6560]
        ),
        new Paragraph({ spacing: { before: 240, after: 120 }, children: [
          new TextRun({ text: "Analysis Methodology: ", bold: true, size: 20, color: NAVY }),
          new TextRun({ text: "All metrics in this report were computed via exact full-table SQL scans in DuckDB 2.0.0 over all 10,000,000 rows (zero sampling bias for counts, sums, medians, or quantiles), supplemented by a 200,000-row reservoir sample for regex token-tag extraction.", size: 20, color: TEXT_MUTED }),
        ]}),
        new Paragraph({ children: [new PageBreak()] }),

        // SECTION 1: WHAT IS THIS DATASET
        h1("1. What Is This Dataset?"),
        p("The file swift_umdac_datathon_2026_fictitious_payment_data.csv is a 4.72 GB synthetic payment-messaging dataset created by Swift for the Universiti Malaya Data Analytics Competition (UMDAC) Datathon 2026. It models 10,000,000 timestamped payment instructions generated via hard-coded business rules, NumPy random distributions, and the Python Faker library."),
        p("Conceptually, the dataset represents a directed temporal pseudograph of global financial flows flattened into tabular form: each row is a payment edge connecting an ordering party (sender) and ordering bank (ORDERING_BIC8) to a beneficiary party (receiver) and beneficiary bank (BENEFICIARY_BIC8) across a multi-hop correspondent banking path (BIC8_PATH)."),
        callout(
          "Important Note on Synthetic Realism & Embedded Disclaimer",
          "The DISCLAIMER column is populated exclusively on Row 1 (9,999,999 NULLs) and states that all records are purely fictitious. While market dynamics, causal routing rules, and fraud patterns are modeled on real-world payment behavior, country populations, city sizes, and economic proportions are intentionally randomized to protect confidential Swift network metrics."
        ),

        h2("1.1 Complete 21-Column Schema & Data Quality"),
        p("Full-table null-check profiling confirms exceptional structural integrity: 19 of the 21 columns contain zero NULL values across all 10,000,000 rows. Only DISCLAIMER (populated on row 1 only) and ANOMALY_TYPE (NULL for 9,992,994 normal transactions) contain NULLs. Note that ORDERING_DETAILS and BENEFICIARY_DETAILS contain embedded newline characters inside RFC-4180 double-quoted fields, expanding the 10M logical records into 83.81M physical file lines."),
        makeTable(
          ["Column Name", "Type", "Nulls", "Purpose & Observed Characteristics"],
          [
            ["DISCLAIMER", "VARCHAR", "9,999,999", "Legal notice on row 1 only; NULL on all remaining 9,999,999 rows."],
            ["EPOCH_SECONDS", "BIGINT", "0", "Unix timestamp (1,682,853,746 to 1,690,797,361 -> Apr 30 to Jul 31, 2023 UTC)."],
            ["CURRENCY_CODE", "VARCHAR", "0", "155 distinct ISO 4217 currency codes; EUR (32.0%) and USD (17.0%) lead."],
            ["USD_AMOUNT", "DOUBLE", "0", "Amount normalized to USD ($0.01 to $15.66B; median $3,661.90; mean $97,204.10)."],
            ["ORDERING_BIC8", "VARCHAR", "0", "8,392 distinct 8-char sending bank BICs; chars 5-6 encode ISO country code."],
            ["BENEFICIARY_BIC8", "VARCHAR", "0", "8,266 distinct 8-char receiving bank BICs; chars 5-6 encode ISO country code."],
            ["BIC8_PATH", "VARCHAR", "0", "Semicolon-separated BIC8 route; contains '...' when CONTINUITY_QFLAG = 'N'."],
            ["TOTAL_DURATION", "BIGINT", "0", "Elapsed settlement duration in seconds (2s to 21,649s; median 56s; mean 771.5s)."],
            ["CONTINUITY_QFLAG", "VARCHAR", "0", "'Y' (92.33%, continuous path) or 'N' (7.67%, gap/hidden intermediary '...')."],
            ["CURRENCY_CONVERSION_COUNT", "BIGINT", "0", "FX conversion steps along route (0 to 17; 1 step = 58.96%, 2 steps = 20.18%)."],
            ["PARTICIPANT_COUNT", "BIGINT", "0", "Banks in route (2 to 22; 2 = 63.23% Direct, 3 = 23.24%, 4+ = 13.53%)."],
            ["TRANSACTION_TYPE_CODE", "VARCHAR", "0", "Routing mode: Direct (63.23%), Indirect (32.61%), Covered (4.16%)."],
            ["ORDERING_ACCOUNT", "VARCHAR", "0", "391,132 distinct synthetic sender IDs (_FAKE_##### pattern)."],
            ["BENEFICIARY_ACCOUNT", "VARCHAR", "0", "2,590,877 distinct synthetic receiver IDs (_FAKE_##### pattern)."],
            ["ORDERING_DETAILS", "VARCHAR", "0", "Raw multi-line remittance/party text (account, name/business, address)."],
            ["ORDERING_TOKENS", "VARCHAR", "0", "Engineered semantic pattern tokens extracted from ORDERING_DETAILS."],
            ["BENEFICIARY_DETAILS", "VARCHAR", "0", "Raw multi-line beneficiary party text (account, name/business, address)."],
            ["BENEFICIARY_TOKENS", "VARCHAR", "0", "Engineered semantic pattern tokens extracted from BENEFICIARY_DETAILS."],
            ["ORDERING_TYPE", "VARCHAR", "0", "'B' (Business, 78.75%) or 'C' (Consumer, 21.25%)."],
            ["BENEFICIARY_TYPE", "VARCHAR", "0", "'C' (Consumer, 71.18%) or 'B' (Business, 28.82%)."],
            ["ANOMALY_TYPE", "VARCHAR", "9,992,994", "6 labeled anomaly classes (7,006 rows = 0.0701%); NULL = normal payment."],
          ],
          [2400, 1000, 1100, 4860]
        ),
        new Paragraph({ children: [new PageBreak()] }),

        // SECTION 2: PARTY FLOW CATEGORIES
        h1("2. Party Flow Categories (B2C, B2B, C2C, C2B)"),
        p("Combining ORDERING_TYPE (B = Business, C = Consumer) and BENEFICIARY_TYPE yields four fundamental economic flow categories. A striking asymmetry defines the dataset: Businesses initiate 78.75% of all transactions, while Consumers receive 71.18% of them—creating a classic payroll/disbursement-heavy count profile (B2C = 56.04%) contrasted against a B2B-dominated value profile (72.54% of total USD volume)."),
        makeTable(
          ["Flow Category", "Count", "Count %", "Median USD", "Mean USD", "Total Volume (USD)", "Volume %"],
          p1.party_pair.map((r) => [
            r.flow_type,
            fmtInt(r.cnt),
            r.pct.toFixed(2) + "%",
            fmtUsd(r.med_usd),
            fmtUsd(r.avg_usd),
            fmtB(r.total_usd),
            ((100 * r.total_usd) / p1.overview.sum_usd).toFixed(2) + "%",
          ]),
          [1300, 1400, 1000, 1300, 1460, 1700, 1200],
          new Set([1, 2, 3, 4, 5, 6])
        ),
        ...addChart("chart1_flow_types.png", "Figure 1: Share of transaction count vs. total USD volume across the four party flow categories.", 520, 260),
        bullet("B2B (Business-to-Business): ", "Only 22.71% of transactions, yet accounts for $705.14B (72.54% of all value) with a median payment of $22,887.71—nearly 50x higher than C2C."),
        bullet("B2C (Business-to-Consumer): ", "The largest category by count (5.60M rows, 56.04%), representing corporate payouts, salaries, and refunds with a median of $3,119.00."),
        bullet("C2C (Consumer-to-Consumer): ", "15.15% of transactions (1.51M rows) with the smallest ticket sizes (median $463.17, 1.30% of total value)."),
        bullet("C2B (Consumer-to-Business): ", "The smallest category by count (6.11%, 610,605 rows), with a median of $3,229.06 (tuition, high-value retail, services)."),
        bullet("Structural Independence Rule: ", "Cross-tabulating flow_type against TRANSACTION_TYPE_CODE reveals exact independence: every flow category routes at ~63.2% Direct, ~32.6% Indirect, and ~4.1% Covered."),

        // SECTION 3: CURRENCIES & GEOGRAPHY
        h1("3. Currency & Geographic Categories"),
        p("The dataset spans 155 ISO 4217 currencies and over 8,200 distinct BIC8 institutions. Encoding of country codes follows the standard ISO 9362 BIC8 structure where characters 5-6 specify the ISO 3166-1 alpha-2 country code (e.g., US, CH, GB, FR, DE, SG)."),
        h2("3.1 Top 15 Payment Currencies"),
        p("EUR and USD together account for 49.02% of all transactions and 59.46% ($577.98B) of total USD value. The top 10 currencies represent 80.17% of transaction volume."),
        makeTable(
          ["Rank", "Currency", "Count", "Count %", "Median USD", "Mean USD", "Total Volume"],
          p1.currencies.slice(0, 15).map((r, i) => [
            i + 1,
            r.CURRENCY_CODE,
            fmtInt(r.cnt),
            r.pct.toFixed(2) + "%",
            fmtUsd(r.med_usd),
            fmtUsd(r.avg_usd),
            fmtB(r.total_usd),
          ]),
          [700, 1000, 1400, 1000, 1400, 1560, 2300],
          new Set([0, 2, 3, 4, 5, 6])
        ),
        ...addChart("chart2_currencies_countries.png", "Figure 2: Top 12 payment currencies (left) and top 12 ordering countries extracted from BIC8 (right).", 560, 245),

        h2("3.2 Domestic vs. Cross-Border & Top Corridors"),
        p("Cross-border payments (where ordering BIC8 country != beneficiary BIC8 country) constitute 92.89% of the dataset (9,288,884 rows), while domestic payments represent 7.11% (711,116 rows). Same-institution transfers (ORDERING_BIC8 = BENEFICIARY_BIC8) are extremely rare at 2,387 rows (0.024%)."),
        makeTable(
          ["Geographic Scope", "Count", "Share %", "Median USD", "Median Dur", "Avg FX Steps", "Avg Participants"],
          p2.domestic_vs_crossborder.map((r) => [
            r.scope,
            fmtInt(r.cnt),
            r.pct.toFixed(2) + "%",
            fmtUsd(r.med_usd),
            r.med_dur + "s",
            r.avg_fx.toFixed(3),
            r.avg_part.toFixed(3),
          ]),
          [2300, 1300, 900, 1300, 1100, 1200, 1260],
          new Set([1, 2, 3, 4, 5, 6])
        ),
        p("The top 5 corridors by transaction count are US -> US (385,598; 3.86%), CH -> US (135,698; 1.36%), GB -> US (129,737; 1.30%), US -> CH (116,603; 1.17%), and FR -> US (96,910; 0.97%). Notably, domestic payments show a higher median value ($5,669 vs. $3,529) and higher median duration (167s vs. 55s), while cross-border payments average 1.382 FX conversions vs. 0.830 for domestic."),
        new Paragraph({ children: [new PageBreak()] }),

        // SECTION 4: ROUTING, CONTINUITY & FX ARCHITECTURE
        h1("4. Routing, Continuity & FX Conversion Mechanics"),
        p("Analysis of TRANSACTION_TYPE_CODE, PARTICIPANT_COUNT, CURRENCY_CONVERSION_COUNT, and CONTINUITY_QFLAG exposes deterministic causal rules embedded in the data generator:"),
        makeTable(
          ["Routing Type", "Count", "Share %", "Median Dur", "Mean Dur", "Avg Participants", "Avg FX Steps"],
          p1.transaction_type.map((r) => [
            r.TRANSACTION_TYPE_CODE,
            fmtInt(r.cnt),
            r.pct.toFixed(2) + "%",
            r.med_dur + "s",
            r.avg_dur.toFixed(1) + "s",
            r.avg_participants.toFixed(3),
            r.avg_fx.toFixed(3),
          ]),
          [1600, 1300, 1000, 1200, 1200, 1560, 1500],
          new Set([1, 2, 3, 4, 5, 6])
        ),
        ...addChart("chart3_routing_fx.png", "Figure 3: Routing category shares (left) and FX conversion count distributions by routing type (right).", 560, 230),
        bullet("Deterministic Direct-Path Rule: ", "Every single Direct payment (6,323,280 rows = 63.2328%) has PARTICIPANT_COUNT = 2, and vice versa. Direct payments never exceed 1 FX conversion (15.69% have 0, 84.31% have 1, 0.00% have >= 2)."),
        bullet("Indirect & Covered Symmetry: ", "Both Indirect (32.61%) and Covered (4.16%) routes average exactly 3.582 participants and ~2.20 FX steps, peaking sharply at 2 FX conversions (55.4% for Indirect, 55.8% for Covered) and extending up to 17 FX steps and 22 participants."),
        bullet("Continuity Flag (CONTINUITY_QFLAG): ", "92.33% of routes are continuous ('Y'), while 7.67% (767,204 rows) are discontinuous ('N', containing '...' in BIC8_PATH). Discontinuous paths are more common in Indirect (12.29% N) and Covered (12.32% N) than Direct (4.99% N), and carry higher participant counts (3.12 vs. 2.54)."),

        // SECTION 5: AMOUNT, DURATION & TEMPORAL DYNAMICS
        h1("5. Value Distribution, Settlement Duration & Temporal Patterns"),
        h2("5.1 Extreme Heavy-Tail Payment Values"),
        p("USD_AMOUNT exhibits an extreme right-skewed distribution: the median payment is $3,661.90 (IQR: $634.09 to $19,959.86), yet the mean is $97,204.10. Just 7,586 payments >= $10M (0.08% of rows) generate $339.99B—34.98% of total dataset volume—heavily inflated by FAT_FINGER_MISTAKE anomalies."),
        makeTable(
          ["USD Amount Bracket", "Transaction Count", "Count %", "Total Volume ($B)", "Volume %"],
          p3.amount_buckets.map((r) => [
            r.bucket,
            fmtInt(r.cnt),
            r.pct.toFixed(2) + "%",
            "$" + Number(r.total_usd_B).toFixed(3) + "B",
            ((100 * Number(r.total_usd_B)) / 972.041).toFixed(2) + "%",
          ]),
          [2200, 2000, 1500, 1900, 1760],
          new Set([1, 2, 3, 4])
        ),
        ...addChart("chart4_amount_duration.png", "Figure 4: USD amount brackets (left) and bimodal settlement duration buckets (right).", 560, 235),

        h2("5.2 Bimodal Settlement Duration"),
        p("TOTAL_DURATION is strongly bimodal rather than unimodal: 53.92% of payments settle within 2 minutes (<30s: 30.35%; 30s-2m: 23.57%), while a second major cluster of 28.53% settles between 10 minutes and 1 hour (and 4.21% >= 1 hour). This reflects fast-rail/STP Direct settlements (median 39s) versus multi-hop Indirect/Covered correspondent chains (median 281s-383s) and compliance/manual holds."),

        h2("5.3 Weekly & Intraday Temporal Rhythms"),
        p("Transactions span April 30 to July 31, 2023 (May: 30.44%, June: 40.50%, July: 28.99%, April 30 partial: 0.06%). Activity follows global banking-hour cycles:"),
        ...addChart("chart5_temporal.png", "Figure 5: Day-of-week volume drop on weekends (left) and UTC hourly activity wave (right).", 560, 225),
        bullet("Weekday vs. Weekend Drop: ", "Monday through Friday each carry 17.05% to 18.34% of weekly volume, whereas Saturday plunges to 4.35% and Sunday to 6.84% (consistent with TARGET2/Fedwire/CHIPS settlement closures)."),
        bullet("Intraday UTC Waves: ", "Volume troughs at 03:00 UTC (218K rows), rises during European opening (06:00-09:00 UTC, ~480K/hr), and peaks during the Europe-US overlap (15:00-17:00 UTC, up to 585.9K/hr)."),
        new Paragraph({ children: [new PageBreak()] }),

        // SECTION 6: TOKENIZED TEXT FEATURES
        h1("6. Party Details & Tokenized Text Features (*_TOKENS)"),
        p("ORDERING_DETAILS and BENEFICIARY_DETAILS store raw multi-line Swift remittance strings. The companion columns ORDERING_TOKENS and BENEFICIARY_TOKENS replace sensitive or variable substrings with typed semantic tags. Across a 200,000-row sample, 19 distinct tag families appear:"),
        makeTable(
          ["Token Tag Category", "Sample Occurrences", "Semantic Meaning"],
          [
            ["<chr:...>", "529,061", "Alphanumeric character-shape masks (e.g., <chr:99-9999>, <chr:A99A>)."],
            ["<street:N>", "284,302", "Street address segment of length N."],
            ["<city:CC:N>", "265,812", "City name tagged with 2-letter country code CC and length N."],
            ["<country_code:CC>", "243,894", "ISO 3166-1 alpha-2 country code."],
            ["<line_break:N>", "204,431", "Explicit line-break / field-separator marker."],
            ["<iban:N>", "200,449", "International Bank Account Number of length N (commonly 22)."],
            ["<business:N>", "184,001", "Corporate/business entity name of length N."],
            ["<post_code:CC:N>", "177,934", "Postal/ZIP code with country code CC and length N."],
            ["<last_name:N> / <first_name:N>", "286,476", "Individual person name components (175,256 last + 111,220 first)."],
            ["<company_keyword:N>", "56,839", "Legal entity suffixes (PLC, LLC, Ltd, GmbH, Inc)."],
            ["<finance_word:...>", "51,051", "Financial keywords (e.g., bank, finance, trust)."],
            ["<separator:...> / <numerical:N>", "86,427", "Punctuation delimiters and pure numeric strings."],
          ],
          [2600, 1800, 4960],
          new Set([1])
        ),

        // SECTION 7: ANOMALY TAXONOMY & FORENSICS
        h1("7. Anomaly Taxonomy & Causal Forensics (7,006 Labeled Records)"),
        p("Exactly 7,006 transactions (0.0701%) carry a non-NULL ANOMALY_TYPE label. Crucially, full-dataset profiling reveals 6 distinct anomaly categories—including CUSTOMER_RECALL (317 rows), which is absent from the Datathon Case Study PDF Appendix."),
        makeTable(
          ["Anomaly Category", "Count", "Share of Anom.", "Median USD", "Mean USD", "Median Dur", "Cross-Border %"],
          p1.anomaly_type.filter((r) => r.category !== "NORMAL (NULL)").map((r) => {
            const fxRow = p3.anomaly_fx_and_crossborder.find((x) => x.anomaly === r.category) || {};
            return [
              r.category,
              fmtInt(r.cnt),
              ((100 * r.cnt) / 7006).toFixed(1) + "%",
              fmtUsd(r.med_usd),
              fmtUsd(r.avg_usd),
              r.med_dur + "s",
              (fxRow.pct_crossborder ?? 0).toFixed(2) + "%",
            ];
          }),
          [2360, 900, 1050, 1250, 1450, 1100, 1250],
          new Set([1, 2, 3, 4, 5, 6])
        ),
        ...addChart("chart6_anomalies.png", "Figure 6: Anomaly record counts (left) and median USD amounts on a log scale vs. normal baseline (right).", 560, 225),

        h2("7.1 Forensic Signatures of Each Anomaly Category"),
        bullet("ROMANCE_SCAM (2,476 rows | 35.3% of anomalies): ", "100% Consumer-originated (73.1% C2C, 26.9% C2B; 0% Business-originated). Concentrated across only 500 distinct sender accounts and 378 distinct receiver accounts (~5 payments per victim), 96.97% cross-border, small median value ($109.45), and the longest median duration (1,148s vs. 56s normal)."),
        bullet("FAT_FINGER_MISTAKE (1,940 rows | 27.7% of anomalies): ", "Distributed across all 4 flow types proportionally to normal traffic (B2C 56.6%, B2B 22.9%). Normal settlement duration (median 53s), but decimal/comma placement errors inflate median value 71x to $260,241.23 and mean value to $90.28M—accounting for $175.14B (18.02% of the entire dataset's USD volume)."),
        bullet("CEO_SCAM (945 rows | 13.5% of anomalies): ", "100% Business-originated (72.3% B2C, 27.7% B2B; 0% Consumer-originated). 98.73% cross-border, high value (median $20,602.13, mean $1.38M), and elevated duration (median 741s)."),
        bullet("DUPLICATE_PAYMENT (679 rows | 9.7% of anomalies): ", "All 679 rows collapse into only 185 distinct (ORDERING_ACCOUNT, BENEFICIARY_ACCOUNT, USD_AMOUNT) tuples (~3.67x repetition per tuple), with elevated median duration (261s)."),
        bullet("ACCOUNT_REPLACEMENT_SCAM (649 rows | 9.3% of anomalies): ", "99.38% cross-border across all 4 flow types, median $3,977.30, and 10x elevated median duration (571s)."),
        bullet("CUSTOMER_RECALL (317 rows | 4.5% of anomalies — Undocumented in PDF): ", "Appears across all 4 flow types with normal duration (median 53s) and value (median $3,163.97), but exhibits the highest path discontinuity rate of any category (11.04% CONTINUITY_QFLAG = 'N' vs. 7.67% normal)."),

        // SECTION 8: SUMMARY OF RECONSTRUCTED RULES
        h1("8. Reverse-Engineered Generating Rules, Causal Relationships & Economic Logic"),
        p("Synthesizing all 10M-row empirical tests (Passes 1-4), the synthetic Swift payment generator is governed by nine concrete causal rules:"),
        bullet("Rule 1 — Account-Level Role Permanence (100% Purity): ", "Every ORDERING_ACCOUNT (391,132 of 391,132 = 100.00%) has a single immutable ORDERING_TYPE ('B' or 'C'). Entity type is an intrinsic property of the account node, not sampled per transaction."),
        bullet("Rule 2 — Sender Home-Currency Dominance (84%-94.5%): ", "Payments overwhelmingly use the ordering country's domestic currency (DE 94.5% EUR, FR 94.0% EUR, US 90.5% USD, CH 88.8% CHF, GB 88.6% GBP, JP 88.3% JPY, SG 87.6% SGD, CN 86.2% CNY). Economic logic: exporters and corporates invoice and initiate wires in their home operating currency, pushing FX conversion downstream."),
        bullet("Rule 3 — Local-Timezone Business-Hour Modulation: ", "Ordering countries peak during their local business hours in UTC: Asia-Pacific (AU 46.4%, JP 41.9%, CN 41.5%, SG 40.7%) concentrates in 00:00-07:59 UTC; Europe (DE 43.0%, CH 42.7%, GB 41.3%) in 08:00-15:59 UTC; US (46.7%) in 16:00-23:59 UTC. Global volume drops ~75% on weekends (Sat 4.35%, Sun 6.84% vs. Mon/Fri 18.34%)."),
        bullet("Rule 4 — Hop-Count Linear Duration Law (~200s/hop): ", "PARTICIPANT_COUNT—not FX count—drives settlement latency: mean duration scales linearly by ~200s per additional intermediary bank (2 hops: 663s; 3: 841s; 4: 1,042s; 5: 1,242s; 6: 1,437s; 7: 1,649s)."),
        bullet("Rule 5 — Direct-Route Structural Ceiling: ", "Direct payments (63.23%) strictly enforce PARTICIPANT_COUNT = 2 and CURRENCY_CONVERSION_COUNT in {0, 1} (0.00% have >= 2 FX steps). Multi-hop Indirect (32.61%) and Covered (4.16%) routes average 3.582 participants and peak at 2 FX conversions (~55.5%)."),
        bullet("Rule 6 — Flow-Type vs. Routing Independence: ", "Party role (B2B, B2C, C2B, C2C) strongly governs payment value (B2B median $22,888 vs. C2C $463) and anomaly eligibility, but is statistically independent of routing mode (~63.2% Direct across all 4 flow types)."),
        bullet("Rule 7 — Role-Gated Social Engineering (ROMANCE_SCAM & CEO_SCAM): ", "ROMANCE_SCAM (2,476 rows) is 100% Consumer-originated (C2C/C2B), concentrated across only 500 senders and 378 mule receivers (~5 wires/victim, median $109.45, median 1,148s). CEO_SCAM (945 rows) is 100% Business-originated (B2C/B2B), 98.73% cross-border, median $20,602."),
        bullet("Rule 8 — Operational Error & Replay Mechanics: ", "FAT_FINGER_MISTAKE (1,940 rows) preserves normal routing/duration (median 53s) but inflates median value 71x ($260,241; $175.14B total = 18.02% of all dataset volume). DUPLICATE_PAYMENT (679 rows) replays 185 exact (sender, receiver, amount) tuples within 0 to 6,940s (median 1,099s / 18.3 min)."),
        bullet("Rule 9 — Discontinuous Path & Recall Coupling: ", "CUSTOMER_RECALL (317 rows, undocumented in the PDF Appendix) exhibits the highest path discontinuity rate (11.04% CONTINUITY_QFLAG = 'N' vs. 7.67% normal)."),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(OUT_DOCX, buffer);
  console.log("Generated:", OUT_DOCX, "Size:", (buffer.length / 1024).toFixed(1), "KB");
});
