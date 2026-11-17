import duckdb
import json
import time

CSV_PATH = "/home/blakie/Downloads/[Participants] Datathon 2026 Materials/swift_umdac_datathon_2026_fictitious_payment_data.csv"
OUT_PATH = "/home/blakie/.gemini/antigravity-cli/brain/9207bfc3-2551-4cda-ad91-4687664bef3f/scratch/pass3_summary.json"

t0 = time.time()
con = duckdb.connect()
con.execute("PRAGMA threads=8;")
con.execute("PRAGMA memory_limit='6GB';")

con.execute(f"""
CREATE VIEW payments AS
SELECT *,
    SUBSTR(ORDERING_BIC8, 5, 2) AS ord_ctry,
    SUBSTR(BENEFICIARY_BIC8, 5, 2) AS ben_ctry,
    ORDERING_TYPE || '2' || BENEFICIARY_TYPE AS flow_type
FROM read_csv(
    '{CSV_PATH}',
    header=true,
    delim=',',
    quote='"',
    escape='"',
    ignore_errors=false,
    sample_size=20000
);
""")

results = {}

queries = {
    "amount_buckets": """
        SELECT CASE
            WHEN USD_AMOUNT < 100 THEN '< $100'
            WHEN USD_AMOUNT < 1000 THEN '$100 - $1K'
            WHEN USD_AMOUNT < 10000 THEN '$1K - $10K'
            WHEN USD_AMOUNT < 100000 THEN '$10K - $100K'
            WHEN USD_AMOUNT < 1000000 THEN '$100K - $1M'
            WHEN USD_AMOUNT < 10000000 THEN '$1M - $10M'
            ELSE '>= $10M'
        END AS bucket,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / 10000000.0, 2) AS pct,
        ROUND(SUM(USD_AMOUNT) / 1e9, 3) AS total_usd_B
        FROM payments
        GROUP BY 1
        ORDER BY MIN(USD_AMOUNT)
    """,
    "duration_buckets": """
        SELECT CASE
            WHEN TOTAL_DURATION < 30 THEN '< 30s'
            WHEN TOTAL_DURATION < 120 THEN '30s - 2m'
            WHEN TOTAL_DURATION < 600 THEN '2m - 10m'
            WHEN TOTAL_DURATION < 3600 THEN '10m - 1h'
            ELSE '>= 1h'
        END AS dur_bucket,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / 10000000.0, 2) AS pct
        FROM payments
        GROUP BY 1
        ORDER BY MIN(TOTAL_DURATION)
    """,
    "anomaly_by_flow_all": """
        SELECT ANOMALY_TYPE, flow_type, COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY ANOMALY_TYPE), 1) AS pct_of_anom,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd
        FROM payments
        WHERE ANOMALY_TYPE IS NOT NULL
        GROUP BY 1, 2 ORDER BY 1, cnt DESC
    """,
    "anomaly_fx_and_crossborder": """
        SELECT COALESCE(ANOMALY_TYPE, 'NORMAL') AS anomaly,
               ROUND(100.0 * AVG(CASE WHEN ord_ctry != ben_ctry THEN 1 ELSE 0 END), 2) AS pct_crossborder,
               ROUND(AVG(CURRENCY_CONVERSION_COUNT), 3) AS avg_fx,
               ROUND(AVG(PARTICIPANT_COUNT), 3) AS avg_part,
               ROUND(100.0 * AVG(CASE WHEN CONTINUITY_QFLAG = 'N' THEN 1 ELSE 0 END), 2) AS pct_discontinuous
        FROM payments
        GROUP BY 1 ORDER BY 1
    """,
    "fx_vs_direct_indirect": """
        SELECT TRANSACTION_TYPE_CODE, CURRENCY_CONVERSION_COUNT,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY TRANSACTION_TYPE_CODE), 2) AS pct_within_type
        FROM payments
        WHERE CURRENCY_CONVERSION_COUNT <= 5
        GROUP BY 1, 2 ORDER BY 1, 2
    """,
    "token_tag_counts_sample": """
        WITH sample_tok AS (
            SELECT ORDERING_TOKENS, BENEFICIARY_TOKENS
            FROM payments USING SAMPLE 200000 ROWS (reservoir, 123)
        ),
        tags AS (
            SELECT UNNEST(REGEXP_EXTRACT_ALL(ORDERING_TOKENS || ' ' || BENEFICIARY_TOKENS, '<([a-z_]+):')) AS tag
            FROM sample_tok
        )
        SELECT tag, COUNT(*) AS cnt
        FROM tags
        GROUP BY 1 ORDER BY cnt DESC
    """,
    "romance_scam_details": """
        SELECT COUNT(*) AS total_rows,
               COUNT(DISTINCT ORDERING_ACCOUNT) AS distinct_senders,
               COUNT(DISTINCT BENEFICIARY_ACCOUNT) AS distinct_receivers,
               MIN(USD_AMOUNT) AS min_usd, MAX(USD_AMOUNT) AS max_usd
        FROM payments WHERE ANOMALY_TYPE = 'ROMANCE_SCAM'
    """,
    "duplicate_payment_check": """
        WITH dups AS (
            SELECT ORDERING_ACCOUNT, BENEFICIARY_ACCOUNT, CURRENCY_CODE, USD_AMOUNT,
                   EPOCH_SECONDS, ANOMALY_TYPE
            FROM payments WHERE ANOMALY_TYPE = 'DUPLICATE_PAYMENT'
        )
        SELECT COUNT(*) AS dup_rows,
               COUNT(DISTINCT ORDERING_ACCOUNT || '|' || BENEFICIARY_ACCOUNT || '|' || CAST(USD_AMOUNT AS VARCHAR)) AS distinct_tuples
        FROM dups
    """
}

for name, q in queries.items():
    df = con.execute(q).fetchdf()
    results[name] = df.to_dict(orient="records")
    print(f"\n=== {name} ===")
    print(df.to_string(index=False))

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nDone in {time.time() - t0:.2f}s")
