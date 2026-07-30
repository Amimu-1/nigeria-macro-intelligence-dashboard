import sqlite3
import pandas as pd

conn = sqlite3.connect("data/database/nigeria_macro.db")

query = """
SELECT
    d.date,
    d.year,
    d.month_name,
    c.headline_inflation_yoy AS cbn_headline_yoy,
    n.inflation_yoy AS nbs_yoy
FROM dim_date d
LEFT JOIN fact_cbn_inflation c ON d.date_id = c.date_id
LEFT JOIN fact_nbs_cpi n ON d.date_id = n.date_id
ORDER BY d.date DESC
LIMIT 10
"""

result = pd.read_sql(query, conn)
print(result.to_string())
conn.close()