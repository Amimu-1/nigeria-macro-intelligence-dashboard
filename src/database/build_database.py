import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = "data/database/nigeria_macro.db"

def build_dim_date(conn, all_dates):
    """Creates a date dimension table from all unique dates across sources."""
    dim_date = pd.DataFrame({"date": sorted(all_dates.unique())})
    dim_date["date_id"] = dim_date.index + 1
    dim_date["year"] = pd.to_datetime(dim_date["date"]).dt.year
    dim_date["month"] = pd.to_datetime(dim_date["date"]).dt.month
    dim_date["quarter"] = pd.to_datetime(dim_date["date"]).dt.quarter
    dim_date["month_name"] = pd.to_datetime(dim_date["date"]).dt.strftime("%B")

    dim_date = dim_date[["date_id", "date", "year", "month", "quarter", "month_name"]]
    dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)
    print(f"dim_date created: {len(dim_date)} rows")
    return dim_date

def build_fact_table(conn, df, dim_date, table_name, value_cols):
    """Joins a cleaned dataframe to dim_date and writes it as a fact table."""
    df = df.copy()
    df["date"] = df["date"].astype(str)
    dim_date_lookup = dim_date.copy()
    dim_date_lookup["date"] = dim_date_lookup["date"].astype(str)

    merged = df.merge(dim_date_lookup[["date_id", "date"]], on="date", how="left")
    keep_cols = ["date_id"] + value_cols
    merged = merged[keep_cols]

    merged.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"{table_name} created: {len(merged)} rows")

def main():
    Path("data/database").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # Load cleaned CSVs
    cbn = pd.read_csv("data/processed/cbn_inflation_clean.csv", parse_dates=["date"])
    nbs = pd.read_csv("data/processed/nbs_cpi_clean.csv", parse_dates=["date"])

    # Build date dimension from combined date range of both sources
    all_dates = pd.concat([cbn["date"], nbs["date"]])
    dim_date = build_dim_date(conn, all_dates)

    # Build fact tables
    build_fact_table(
        conn, cbn, dim_date, "fact_cbn_inflation",
        ["headline_inflation_yoy", "headline_inflation_avg",
         "food_inflation_yoy", "food_inflation_avg",
         "core_inflation_yoy", "core_inflation_avg",
         "core_ex_energy_yoy", "core_ex_energy_avg"]
    )

    build_fact_table(
        conn, nbs, dim_date, "fact_nbs_cpi",
        ["cpi_index", "inflation_yoy"]
    )

    conn.close()
    print(f"\nDatabase built successfully at {DB_PATH}")

if __name__ == "__main__":
    main()