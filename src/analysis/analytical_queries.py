import sqlite3
import pandas as pd

DB_PATH = "data/database/nigeria_macro.db"

def run_query(query: str, description: str):
    conn = sqlite3.connect(DB_PATH)
    print(f"\n{'='*70}")
    print(f"QUERY: {description}")
    print(f"{'='*70}")
    result = pd.read_sql(query, conn)
    print(result.to_string())
    conn.close()
    return result

# ─────────────────────────────────────────────────────────
# QUERY 1: Master monthly view — inflation, exchange rate, reserves
# ─────────────────────────────────────────────────────────
QUERY_1 = """
SELECT
    d.date,
    d.year,
    d.month_name,
    c.headline_inflation_yoy AS cbn_inflation_yoy,
    n.inflation_yoy AS nbs_inflation_yoy,
    fx.exchange_rate,
    r.external_reserves_usd_million
FROM dim_date d
LEFT JOIN fact_cbn_inflation c ON d.date_id = c.date_id
LEFT JOIN fact_nbs_cpi n ON d.date_id = n.date_id
LEFT JOIN fact_exchange_rate fx ON d.date_id = fx.date_id
LEFT JOIN fact_reserves r ON d.date_id = r.date_id
WHERE fx.exchange_rate IS NOT NULL
ORDER BY d.date DESC
LIMIT 15
"""

# ─────────────────────────────────────────────────────────
# QUERY 2: Inflation trend with 3-month moving average
# ─────────────────────────────────────────────────────────
QUERY_2 = """
WITH inflation_series AS (
    SELECT
        d.date,
        c.headline_inflation_yoy AS inflation_yoy
    FROM dim_date d
    JOIN fact_cbn_inflation c ON d.date_id = c.date_id
    WHERE c.headline_inflation_yoy IS NOT NULL
)
SELECT
    date,
    inflation_yoy,
    ROUND(AVG(inflation_yoy) OVER (
        ORDER BY date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS moving_avg_3month
FROM inflation_series
ORDER BY date DESC
LIMIT 15
"""

# ─────────────────────────────────────────────────────────
# QUERY 3: CBN vs NBS inflation gap, quantified month by month
# ─────────────────────────────────────────────────────────
QUERY_3 = """
SELECT
    d.date,
    c.headline_inflation_yoy AS cbn_inflation_yoy,
    n.inflation_yoy AS nbs_inflation_yoy,
    ROUND(c.headline_inflation_yoy - n.inflation_yoy, 2) AS gap_cbn_minus_nbs
FROM dim_date d
JOIN fact_cbn_inflation c ON d.date_id = c.date_id
JOIN fact_nbs_cpi n ON d.date_id = n.date_id
WHERE c.headline_inflation_yoy IS NOT NULL
  AND n.inflation_yoy IS NOT NULL
ORDER BY d.date DESC
LIMIT 20
"""

# ─────────────────────────────────────────────────────────
# QUERY 4: MPR vs inflation (annual) — real policy rate
# ─────────────────────────────────────────────────────────
QUERY_4 = """
WITH december_inflation AS (
    SELECT
        d.year,
        c.headline_inflation_yoy AS december_inflation_yoy
    FROM dim_date d
    JOIN fact_cbn_inflation c ON d.date_id = c.date_id
    WHERE d.month = 12
)
SELECT
    d.year,
    m.mpr,
    di.december_inflation_yoy,
    ROUND(m.mpr - di.december_inflation_yoy, 2) AS real_policy_rate
FROM dim_date d
JOIN fact_mpr m ON d.date_id = m.date_id
LEFT JOIN december_inflation di ON d.year = di.year
WHERE d.month = 1
ORDER BY d.year
"""

# ─────────────────────────────────────────────────────────
# QUERY 5: Money supply growth (YoY %) vs inflation, annual
# ─────────────────────────────────────────────────────────
QUERY_5 = """
WITH money_supply_growth AS (
    SELECT
        d.year,
        ms.broad_money,
        ROUND(
            (ms.broad_money - LAG(ms.broad_money) OVER (ORDER BY d.year))
            / LAG(ms.broad_money) OVER (ORDER BY d.year) * 100
        , 2) AS money_supply_growth_pct
    FROM dim_date d
    JOIN fact_money_supply ms ON d.date_id = ms.date_id
    WHERE d.month = 12
),
december_inflation AS (
    SELECT
        d.year,
        c.headline_inflation_yoy AS december_inflation_yoy
    FROM dim_date d
    JOIN fact_cbn_inflation c ON d.date_id = c.date_id
    WHERE d.month = 12
)
SELECT
    msg.year,
    msg.broad_money,
    msg.money_supply_growth_pct,
    di.december_inflation_yoy
FROM money_supply_growth msg
LEFT JOIN december_inflation di ON msg.year = di.year
ORDER BY msg.year
"""

# ─────────────────────────────────────────────────────────
# QUERY 6: Post-subsidy-removal impact (May 2023)
# ─────────────────────────────────────────────────────────
QUERY_6 = """
WITH before_period AS (
    SELECT
        AVG(c.headline_inflation_yoy) AS avg_inflation,
        AVG(fx.exchange_rate) AS avg_exchange_rate
    FROM dim_date d
    LEFT JOIN fact_cbn_inflation c ON d.date_id = c.date_id
    LEFT JOIN fact_exchange_rate fx ON d.date_id = fx.date_id
    WHERE d.date >= '2022-06-01' AND d.date < '2023-06-01'
),
after_period AS (
    SELECT
        AVG(c.headline_inflation_yoy) AS avg_inflation,
        AVG(fx.exchange_rate) AS avg_exchange_rate
    FROM dim_date d
    LEFT JOIN fact_cbn_inflation c ON d.date_id = c.date_id
    LEFT JOIN fact_exchange_rate fx ON d.date_id = fx.date_id
    WHERE d.date >= '2023-06-01' AND d.date < '2024-06-01'
)
SELECT
    'Before (Jun 2022 - May 2023)' AS period,
    ROUND(avg_inflation, 2) AS avg_inflation_yoy,
    ROUND(avg_exchange_rate, 2) AS avg_exchange_rate
FROM before_period
UNION ALL
SELECT
    'After (Jun 2023 - May 2024)' AS period,
    ROUND(avg_inflation, 2) AS avg_inflation_yoy,
    ROUND(avg_exchange_rate, 2) AS avg_exchange_rate
FROM after_period
"""

# ─────────────────────────────────────────────────────────
# QUERY 7: Exchange rate vs external reserves relationship
# Tests whether reserve declines coincide with or precede
# currency depreciation, using year-over-year change in both.
# ─────────────────────────────────────────────────────────
QUERY_7 = """
WITH annual_reserves AS (
    SELECT
        d.year,
        AVG(r.external_reserves_usd_million) AS avg_reserves
    FROM dim_date d
    JOIN fact_reserves r ON d.date_id = r.date_id
    GROUP BY d.year
),
annual_fx AS (
    SELECT
        d.year,
        AVG(fx.exchange_rate) AS avg_exchange_rate
    FROM dim_date d
    JOIN fact_exchange_rate fx ON d.date_id = fx.date_id
    WHERE fx.exchange_rate IS NOT NULL
    GROUP BY d.year
)
SELECT
    ar.year,
    ROUND(ar.avg_reserves, 1) AS avg_reserves_usd_million,
    ROUND(
        (ar.avg_reserves - LAG(ar.avg_reserves) OVER (ORDER BY ar.year))
        / LAG(ar.avg_reserves) OVER (ORDER BY ar.year) * 100
    , 2) AS reserves_change_pct,
    ROUND(af.avg_exchange_rate, 2) AS avg_exchange_rate,
    ROUND(
        (af.avg_exchange_rate - LAG(af.avg_exchange_rate) OVER (ORDER BY ar.year))
        / LAG(af.avg_exchange_rate) OVER (ORDER BY ar.year) * 100
    , 2) AS exchange_rate_change_pct
FROM annual_reserves ar
JOIN annual_fx af ON ar.year = af.year
ORDER BY ar.year
"""

# ─────────────────────────────────────────────────────────
# QUERY 8: Banking sector health trend over time
# ─────────────────────────────────────────────────────────
QUERY_8 = """
SELECT
    d.year,
    b.liquidity_ratio,
    b.loan_to_deposit_ratio,
    CASE
        WHEN b.liquidity_ratio >= 30 THEN 'Above Minimum'
        ELSE 'Below Minimum'
    END AS liquidity_status,
    CASE
        WHEN b.loan_to_deposit_ratio <= 80 THEN 'Within Maximum'
        ELSE 'Above Maximum'
    END AS ldr_status
FROM dim_date d
JOIN fact_banking_ratios b ON d.date_id = b.date_id
ORDER BY d.year
"""

if __name__ == "__main__":
    run_query(QUERY_1, "Master Monthly View (most recent 15 months)")
    run_query(QUERY_2, "Inflation Trend with 3-Month Moving Average")
    run_query(QUERY_3, "CBN vs NBS Inflation Gap")
    run_query(QUERY_4, "MPR vs Year-End Inflation (Real Policy Rate)")
    run_query(QUERY_5, "Money Supply Growth vs Inflation (Annual)")
    run_query(QUERY_6, "Post-Subsidy-Removal Impact (May 2023)")
    run_query(QUERY_7, "Exchange Rate vs External Reserves Relationship")
    run_query(QUERY_8, "Banking Sector Health Trend")
