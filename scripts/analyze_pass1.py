import duckdb
import json
import time

CSV_PATH = "/home/blakie/Downloads/[Participants] Datathon 2026 Materials/swift_umdac_datathon_2026_fictitious_payment_data.csv"
OUT_PATH = "/home/blakie/.gemini/antigravity-cli/brain/9207bfc3-2551-4cda-ad91-4687664bef3f/scratch/pass1_summary.json"

t0 = time.time()
con = duckdb.connect()
con.execute("PRAGMA threads=8;")
con.execute("PRAGMA memory_limit='6GB';")

# Create a view over the CSV with explicit handling of multiline quoted fields
con.execute(f"""
CREATE VIEW payments AS
SELECT * FROM read_csv(
    '{CSV_PATH}',
    header=true,
    delim=',',
    quote='"',
    escape='"',
    ignore_errors=false,
    sample_size=20000
);
""")

print("Schema:")
schema = con.execute("DESCRIBE payments").fetchall()
for col in schema:
    print(col)

print("\nRunning total count & numeric summaries...")
summary = {}

# 1. Total rows and numeric stats
row_stats = con.execute("""
SELECT
    COUNT(*) AS total_rows,
    MIN(EPOCH_SECONDS) AS min_epoch,
    MAX(EPOCH_SECONDS) AS max_epoch,
    TO_TIMESTAMP(MIN(EPOCH_SECONDS)) AT TIME ZONE 'UTC' AS min_utc,
    TO_TIMESTAMP(MAX(EPOCH_SECONDS)) AT TIME ZONE 'UTC' AS max_utc,
    MIN(USD_AMOUNT) AS min_usd,
    QUANTILE_CONT(USD_AMOUNT, 0.01) AS p01_usd,
    QUANTILE_CONT(USD_AMOUNT, 0.05) AS p05_usd,
    QUANTILE_CONT(USD_AMOUNT, 0.25) AS p25_usd,
    MEDIAN(USD_AMOUNT) AS p50_usd,
    AVG(USD_AMOUNT) AS avg_usd,
    QUANTILE_CONT(USD_AMOUNT, 0.75) AS p75_usd,
    QUANTILE_CONT(USD_AMOUNT, 0.95) AS p95_usd,
    QUANTILE_CONT(USD_AMOUNT, 0.99) AS p99_usd,
    MAX(USD_AMOUNT) AS max_usd,
    SUM(USD_AMOUNT) AS sum_usd,
    MIN(TOTAL_DURATION) AS min_dur,
    QUANTILE_CONT(TOTAL_DURATION, 0.05) AS p05_dur,
    QUANTILE_CONT(TOTAL_DURATION, 0.25) AS p25_dur,
    MEDIAN(TOTAL_DURATION) AS p50_dur,
    AVG(TOTAL_DURATION) AS avg_dur,
    QUANTILE_CONT(TOTAL_DURATION, 0.75) AS p75_dur,
    QUANTILE_CONT(TOTAL_DURATION, 0.95) AS p95_dur,
    QUANTILE_CONT(TOTAL_DURATION, 0.99) AS p99_dur,
    MAX(TOTAL_DURATION) AS max_dur,
    COUNT(DISTINCT CURRENCY_CODE) AS n_currencies,
    COUNT(DISTINCT ORDERING_BIC8) AS n_ord_bic,
    COUNT(DISTINCT BENEFICIARY_BIC8) AS n_ben_bic,
    COUNT(DISTINCT ORDERING_ACCOUNT) AS n_ord_acct,
    COUNT(DISTINCT BENEFICIARY_ACCOUNT) AS n_ben_acct
FROM payments
""").fetchdf().to_dict(orient="records")[0]
summary["overview"] = {k: str(v) if "Timestamp" in str(type(v)) else v for k, v in row_stats.items()}
print("Overview:", json.dumps(summary["overview"], indent=2, default=str))

# 2. Null / empty checks
cols = [c[0] for c in schema]
null_exprs = ", ".join([f"COUNT(*) - COUNT({c}) AS null_{c}" for c in cols])
null_counts = con.execute(f"SELECT {null_exprs} FROM payments").fetchdf().to_dict(orient="records")[0]
summary["null_counts"] = null_counts
print("Null counts:", null_counts)

# 3. Categorical distributions
queries = {
    "anomaly_type": """
        SELECT COALESCE(ANOMALY_TYPE, 'NORMAL (NULL)') AS category,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd,
               ROUND(SUM(USD_AMOUNT), 2) AS total_usd,
               ROUND(AVG(TOTAL_DURATION), 2) AS avg_dur,
               ROUND(MEDIAN(TOTAL_DURATION), 2) AS med_dur
        FROM payments
        GROUP BY 1 ORDER BY cnt DESC
    """,
    "transaction_type": """
        SELECT TRANSACTION_TYPE_CODE,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd,
               ROUND(AVG(TOTAL_DURATION), 2) AS avg_dur,
               ROUND(MEDIAN(TOTAL_DURATION), 2) AS med_dur,
               ROUND(AVG(PARTICIPANT_COUNT), 3) AS avg_participants,
               ROUND(AVG(CURRENCY_CONVERSION_COUNT), 3) AS avg_fx
        FROM payments
        GROUP BY 1 ORDER BY cnt DESC
    """,
    "continuity_qflag": """
        SELECT CONTINUITY_QFLAG,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(AVG(TOTAL_DURATION), 2) AS avg_dur,
               ROUND(AVG(PARTICIPANT_COUNT), 3) AS avg_participants
        FROM payments
        GROUP BY 1 ORDER BY cnt DESC
    """,
    "party_pair": """
        SELECT ORDERING_TYPE, BENEFICIARY_TYPE,
               ORDERING_TYPE || '2' || BENEFICIARY_TYPE AS flow_type,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd,
               ROUND(SUM(USD_AMOUNT), 2) AS total_usd
        FROM payments
        GROUP BY 1, 2, 3 ORDER BY cnt DESC
    """,
    "currencies": """
        SELECT CURRENCY_CODE,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(MEDIAN(USD_AMOUNT), 2) AS med_usd,
               ROUND(SUM(USD_AMOUNT), 2) AS total_usd
        FROM payments
        GROUP BY 1 ORDER BY cnt DESC
    """,
    "fx_counts": """
        SELECT CURRENCY_CONVERSION_COUNT,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(AVG(TOTAL_DURATION), 2) AS avg_dur
        FROM payments
        GROUP BY 1 ORDER BY 1
    """,
    "participant_counts": """
        SELECT PARTICIPANT_COUNT,
               COUNT(*) AS cnt,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS pct,
               ROUND(AVG(USD_AMOUNT), 2) AS avg_usd,
               ROUND(AVG(TOTAL_DURATION), 2) AS avg_dur
        FROM payments
        GROUP BY 1 ORDER BY 1
    """
}

for name, q in queries.items():
    df = con.execute(q).fetchdf()
    summary[name] = df.to_dict(orient="records")
    print(f"\n--- {name} ---")
    print(df.to_string(index=False))

with open(OUT_PATH, "w") as f:
    json.dump(summary, f, indent=2, default=str)

print(f"\nDone in {time.time() - t0:.2f}s")
