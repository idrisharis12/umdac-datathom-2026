import duckdb
import json
import time

CSV_PATH = "/home/blakie/Downloads/[Participants] Datathon 2026 Materials/swift_umdac_datathon_2026_fictitious_payment_data.csv"
OUT_PATH = "/home/blakie/.gemini/antigravity-cli/brain/9207bfc3-2551-4cda-ad91-4687664bef3f/scratch/pass2_summary.json"

t0 = time.time()
con = duckdb.connect()
con.execute("PRAGMA threads=8;")
con.execute("PRAGMA memory_limit='6GB';")

con.execute(f"""
CREATE VIEW payments AS
SELECT *,
    SUBSTR(ORDERING_BIC8, 5, 2) AS ord_ctry,
    SUBSTR(BENEFICIARY_BIC8, 5, 2) AS ben_ctry,
    ORDERING_TYPE || '2' || BENEFICIARY_TYPE AS flow_type,
    TO_TIMESTAMP(EPOCH_SECONDS) AT TIME ZONE 'UTC' AS utc_ts
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
    "top_ord_countries": """
        SELECT ord_ctry, COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd
        FROM payments GROUP BY 1 ORDER BY cnt DESC LIMIT 25
    """,
    "top_ben_countries": """
        SELECT ben_ctry, COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd
        FROM payments GROUP BY 1 ORDER BY cnt DESC LIMIT 25
    """,
    "domestic_vs_crossborder": """
        SELECT CASE WHEN ord_ctry = ben_ctry THEN 'Domestic (Same Country)' ELSE 'Cross-Border' END AS scope,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd,
               ROUND(AVG(TOTAL_DURATION), 2) AS avg_dur,
               ROUND(MEDIAN(TOTAL_DURATION), 2) AS med_dur,
               ROUND(AVG(CURRENCY_CONVERSION_COUNT), 3) AS avg_fx,
               ROUND(AVG(PARTICIPANT_COUNT), 3) AS avg_part
        FROM payments GROUP BY 1 ORDER BY cnt DESC
    """,
    "same_bic_check": """
        SELECT CASE WHEN ORDERING_BIC8 = BENEFICIARY_BIC8 THEN 'Same BIC8' ELSE 'Different BIC8' END AS bic_rel,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 3) AS pct
        FROM payments GROUP BY 1
    """,
    "top_corridors": """
        SELECT ord_ctry || ' -> ' || ben_ctry AS corridor,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / 10000000.0, 2) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd
        FROM payments GROUP BY 1 ORDER BY cnt DESC LIMIT 20
    """,
    "temporal_dow": """
        SELECT EXTRACT('dow' FROM utc_ts) AS dow_0sun,
               STRFTIME(utc_ts, '%a') AS day_name,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd,
               ROUND(AVG(TOTAL_DURATION), 2) AS avg_dur,
               ROUND(MEDIAN(TOTAL_DURATION), 2) AS med_dur
        FROM payments GROUP BY 1, 2 ORDER BY 1
    """,
    "temporal_hour": """
        SELECT EXTRACT('hour' FROM utc_ts) AS utc_hour,
               COUNT(*) AS cnt,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd,
               ROUND(AVG(TOTAL_DURATION), 2) AS avg_dur,
               ROUND(MEDIAN(TOTAL_DURATION), 2) AS med_dur
        FROM payments GROUP BY 1 ORDER BY 1
    """,
    "temporal_month": """
        SELECT STRFTIME(utc_ts, '%Y-%m') AS ym,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(SUM(USD_AMOUNT), 2) AS total_usd
        FROM payments GROUP BY 1 ORDER BY 1
    """,
    "anomaly_by_flow": """
        SELECT COALESCE(ANOMALY_TYPE, 'NORMAL') AS anomaly,
               flow_type,
               COUNT(*) AS cnt,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd,
               ROUND(AVG(TOTAL_DURATION), 2) AS avg_dur,
               ROUND(MEDIAN(TOTAL_DURATION), 2) AS med_dur
        FROM payments
        WHERE ANOMALY_TYPE IS NOT NULL
        GROUP BY 1, 2 ORDER BY 1, cnt DESC
    """,
    "anomaly_by_txtype_cont": """
        SELECT ANOMALY_TYPE,
               TRANSACTION_TYPE_CODE,
               CONTINUITY_QFLAG,
               COUNT(*) AS cnt
        FROM payments
        WHERE ANOMALY_TYPE IS NOT NULL
        GROUP BY 1, 2, 3 ORDER BY 1, cnt DESC
    """,
    "txtype_x_continuity": """
        SELECT TRANSACTION_TYPE_CODE, CONTINUITY_QFLAG,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct,
               ROUND(AVG(PARTICIPANT_COUNT), 3) AS avg_part,
               ROUND(AVG(TOTAL_DURATION), 2) AS avg_dur,
               ROUND(MEDIAN(TOTAL_DURATION), 2) AS med_dur
        FROM payments GROUP BY 1, 2 ORDER BY 1, 2
    """,
    "flow_x_txtype": """
        SELECT flow_type, TRANSACTION_TYPE_CODE,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY flow_type), 2) AS pct_within_flow
        FROM payments GROUP BY 1, 2 ORDER BY 1, cnt DESC
    """,
    "sample_tokens_and_paths": """
        SELECT TRANSACTION_TYPE_CODE, CONTINUITY_QFLAG, PARTICIPANT_COUNT, BIC8_PATH,
               ORDERING_TYPE, BENEFICIARY_TYPE, ORDERING_TOKENS, BENEFICIARY_TOKENS, ANOMALY_TYPE
        FROM payments
        USING SAMPLE 15 ROWS (reservoir, 42)
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
