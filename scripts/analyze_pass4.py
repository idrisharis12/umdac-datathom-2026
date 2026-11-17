import duckdb
import json
import time

CSV_PATH = "/home/blakie/Downloads/[Participants] Datathon 2026 Materials/swift_umdac_datathon_2026_fictitious_payment_data.csv"
OUT_PATH = "/home/blakie/.gemini/antigravity-cli/brain/9207bfc3-2551-4cda-ad91-4687664bef3f/scratch/pass4_causal_rules.json"

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
    TO_TIMESTAMP(EPOCH_SECONDS) AT TIME ZONE 'UTC' AS utc_ts,
    EXTRACT('hour' FROM TO_TIMESTAMP(EPOCH_SECONDS) AT TIME ZONE 'UTC') AS utc_hour
FROM read_csv(
    '{CSV_PATH}',
    header=true, delim=',', quote='"', escape='"', ignore_errors=false, sample_size=20000
);
""")

res = {}

queries = {
    "duration_by_part_and_fx": """
        SELECT PARTICIPANT_COUNT, CURRENCY_CONVERSION_COUNT, COUNT(*) AS cnt,
               ROUND(MEDIAN(TOTAL_DURATION), 1) AS med_dur,
               ROUND(AVG(TOTAL_DURATION), 1) AS avg_dur,
               ROUND(QUANTILE_CONT(TOTAL_DURATION, 0.25), 1) AS p25_dur,
               ROUND(QUANTILE_CONT(TOTAL_DURATION, 0.75), 1) AS p75_dur
        FROM payments
        WHERE PARTICIPANT_COUNT <= 6 AND CURRENCY_CONVERSION_COUNT <= 4
        GROUP BY 1, 2 ORDER BY 1, 2
    """,
    "timezone_peak_by_country": """
        SELECT ord_ctry,
               COUNT(*) AS total_cnt,
               ROUND(AVG(utc_hour), 2) AS avg_utc_hr,
               ROUND(100.0 * SUM(CASE WHEN utc_hour BETWEEN 0 AND 7 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_00_07_asia,
               ROUND(100.0 * SUM(CASE WHEN utc_hour BETWEEN 8 AND 15 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_08_15_eu,
               ROUND(100.0 * SUM(CASE WHEN utc_hour BETWEEN 16 AND 23 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_16_23_us
        FROM payments
        WHERE ord_ctry IN ('US', 'GB', 'DE', 'CH', 'SG', 'JP', 'CN', 'AU')
        GROUP BY 1 ORDER BY total_cnt DESC
    """,
    "currency_home_match": """
        WITH home_map AS (
            SELECT 'US' AS ctry, 'USD' AS home_cur UNION ALL
            SELECT 'GB', 'GBP' UNION ALL
            SELECT 'CH', 'CHF' UNION ALL
            SELECT 'DE', 'EUR' UNION ALL
            SELECT 'FR', 'EUR' UNION ALL
            SELECT 'IT', 'EUR' UNION ALL
            SELECT 'SG', 'SGD' UNION ALL
            SELECT 'JP', 'JPY' UNION ALL
            SELECT 'CN', 'CNY' UNION ALL
            SELECT 'AU', 'AUD'
        )
        SELECT p.ord_ctry,
               COUNT(*) AS cnt,
               ROUND(100.0 * AVG(CASE WHEN p.CURRENCY_CODE = h1.home_cur THEN 1 ELSE 0 END), 2) AS pct_ord_home_cur,
               ROUND(100.0 * AVG(CASE WHEN p.CURRENCY_CODE = 'USD' THEN 1 ELSE 0 END), 2) AS pct_usd,
               ROUND(100.0 * AVG(CASE WHEN p.CURRENCY_CODE = 'EUR' THEN 1 ELSE 0 END), 2) AS pct_eur
        FROM payments p
        JOIN home_map h1 ON p.ord_ctry = h1.ctry
        GROUP BY 1 ORDER BY cnt DESC
    """,
    "duplicate_time_gaps": """
        WITH d AS (
            SELECT ORDERING_ACCOUNT, BENEFICIARY_ACCOUNT, USD_AMOUNT, EPOCH_SECONDS,
                   LAG(EPOCH_SECONDS) OVER (PARTITION BY ORDERING_ACCOUNT, BENEFICIARY_ACCOUNT, USD_AMOUNT ORDER BY EPOCH_SECONDS) AS prev_ep
            FROM payments
            WHERE ANOMALY_TYPE = 'DUPLICATE_PAYMENT'
        )
        SELECT COUNT(*) AS pairs,
               MIN(EPOCH_SECONDS - prev_ep) AS min_gap_s,
               ROUND(MEDIAN(EPOCH_SECONDS - prev_ep), 1) AS med_gap_s,
               ROUND(AVG(EPOCH_SECONDS - prev_ep), 1) AS avg_gap_s,
               MAX(EPOCH_SECONDS - prev_ep) AS max_gap_s
        FROM d WHERE prev_ep IS NOT NULL
    """,
    "account_type_purity": """
        SELECT COUNT(*) AS total_ord_accts,
               SUM(CASE WHEN n_types = 1 THEN 1 ELSE 0 END) AS pure_single_type_accts
        FROM (
            SELECT ORDERING_ACCOUNT, COUNT(DISTINCT ORDERING_TYPE) AS n_types
            FROM payments GROUP BY 1
        )
    """,
    "amount_round_numbers": """
        SELECT ROUND(100.0 * AVG(CASE WHEN USD_AMOUNT = FLOOR(USD_AMOUNT) THEN 1 ELSE 0 END), 2) AS pct_exact_integer_usd,
               ROUND(100.0 * AVG(CASE WHEN MOD(CAST(USD_AMOUNT AS BIGINT), 100) = 0 AND USD_AMOUNT = FLOOR(USD_AMOUNT) THEN 1 ELSE 0 END), 2) AS pct_mult_100
        FROM payments
    """
}

for name, q in queries.items():
    df = con.execute(q).fetchdf()
    res[name] = df.to_dict(orient="records")
    print(f"\n=== {name} ===")
    print(df.to_string(index=False))

with open(OUT_PATH, "w") as f:
    json.dump(res, f, indent=2, default=str)

print(f"\nDone in {time.time() - t0:.2f}s")
