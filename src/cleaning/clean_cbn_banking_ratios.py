import pandas as pd
from pathlib import Path

def clean_cbn_banking_ratios(raw_path: str, output_path: str):
    """
    Cleans CBN Statistical Bulletin A.13 (Selected Financial Ratios of
    Commercial Banks). Only annual rows are used (year values like 2015);
    quarterly breakdown rows (Q1-Q4) for 2021-2024 are skipped since
    we're using annual granularity, consistent with MPR and money supply.

    Column 1 = Liquidity Ratio (Actual)
    Column 5 = Loan-to-Deposit Ratio (Actual)
    """
    raw = pd.read_excel(raw_path, sheet_name=34, header=None, engine="calamine")

    data = raw.iloc[4:64].copy()
    data.columns = ["period", "liquidity_ratio", "liquidity_min",
                    "crr", "crr_public_funds", "loan_to_deposit_ratio", "ldr_max"]

    # Keep only rows where period is a clean 4-digit year (skip Q1-Q4 rows)
    data["year"] = pd.to_numeric(data["period"], errors="coerce")
    data = data.dropna(subset=["year"])
    data["year"] = data["year"].astype(int)

    data["liquidity_ratio"] = pd.to_numeric(data["liquidity_ratio"], errors="coerce")
    data["loan_to_deposit_ratio"] = pd.to_numeric(data["loan_to_deposit_ratio"], errors="coerce")

    data = data[["year", "liquidity_ratio", "loan_to_deposit_ratio"]]
    data = data.dropna(subset=["liquidity_ratio", "loan_to_deposit_ratio"], how="all")

    # Filter to project window
    data = data[(data["year"] >= 2015) & (data["year"] <= 2025)]

    data["date"] = pd.to_datetime(data["year"].astype(str) + "-12-01")
    data = data[["date", "liquidity_ratio", "loan_to_deposit_ratio"]].sort_values("date").reset_index(drop=True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)

    print(f"Cleaned banking ratios data saved to {output_path}")
    print(f"Rows: {len(data)}, Date range: {data['date'].min()} to {data['date'].max()}")
    print(data)

if __name__ == "__main__":
    clean_cbn_banking_ratios(
        "data/raw/cbn_exchange_rate/statistical_bulletin_financial_sector.xlsx",
        "data/processed/cbn_banking_ratios_clean.csv"
    )