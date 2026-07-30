import pandas as pd
from pathlib import Path

def clean_cbn_mpr(raw_path: str, output_path: str):
    """
    Cleans CBN Statistical Bulletin A11 (Money Market Interest Rates).
    Only annual rows are used (year values like 2015, 2016, etc.);
    quarterly breakdown rows (Q1-Q4) for 2022-2024 are skipped since
    we're using annual granularity for MPR in this project.
    Column 2 = Monetary Policy Rate.
    """
    raw = pd.read_excel(raw_path, sheet_name="A11", header=None, engine="calamine")

    data = raw.iloc[6:62].copy()
    data.columns = ["period", "min_rediscount_rate", "mpr", "treasury_bill_rate",
                    "deposit_3m", "deposit_6m", "deposit_12m", "deposit_over12m"]

    # Keep only rows where period is a clean 4-digit year (skip Q1-Q4 rows)
    data["year"] = pd.to_numeric(data["period"], errors="coerce")
    data = data.dropna(subset=["year"])
    data["year"] = data["year"].astype(int)

    data["mpr"] = pd.to_numeric(data["mpr"], errors="coerce")
    data = data[["year", "mpr"]].dropna(subset=["mpr"])

    # Filter to project window
    data = data[(data["year"] >= 2015) & (data["year"] <= 2025)]

    # Represent as one row per year, dated to January 1 of that year
    data["date"] = pd.to_datetime(data["year"].astype(str) + "-01-01")
    data = data[["date", "mpr"]].sort_values("date").reset_index(drop=True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)

    print(f"Cleaned MPR data saved to {output_path}")
    print(f"Rows: {len(data)}, Date range: {data['date'].min()} to {data['date'].max()}")
    print(data)

if __name__ == "__main__":
    clean_cbn_mpr(
        "data/raw/cbn_exchange_rate/statistical_bulletin_financial_sector.xlsx",
        "data/processed/cbn_mpr_clean.csv"
    )