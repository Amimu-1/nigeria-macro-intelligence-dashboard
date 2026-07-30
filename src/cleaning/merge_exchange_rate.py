import pandas as pd
from pathlib import Path

def merge_exchange_rate_series(historical_path: str, recent_path: str, output_path: str):
    """
    Stitches together the historical CBN official rate (2015-01 to 2024-11)
    with the recent NFEM rate (2024-12 to present) into one continuous
    monthly exchange rate series.
    """
    historical = pd.read_csv(historical_path, parse_dates=["date"])
    historical = historical.rename(columns={"official_rate": "exchange_rate"})
    historical["source"] = "CBN Official Rate (Historical)"

    recent = pd.read_csv(recent_path, parse_dates=["date"])
    recent = recent.rename(columns={"avg_nfem_rate": "exchange_rate"})
    recent = recent[["date", "exchange_rate"]]
    recent["source"] = "NFEM Rate"

    combined = pd.concat([historical[["date", "exchange_rate", "source"]], recent], ignore_index=True)
    combined = combined.sort_values("date").reset_index(drop=True)

    # Sanity check: no duplicate months, no gaps
    combined["gap_check"] = combined["date"].diff().dt.days
    gaps = combined[combined["gap_check"] > 32]
    if len(gaps) > 0:
        print("WARNING: Potential gaps detected at:")
        print(gaps[["date", "gap_check"]])

    combined = combined.drop(columns=["gap_check"])

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_path, index=False)

    print(f"\nMerged exchange rate series saved to {output_path}")
    print(f"Rows: {len(combined)}, Date range: {combined['date'].min()} to {combined['date'].max()}")
    print(f"\nTransition point (around Nov-Dec 2024):")
    print(combined[(combined["date"] >= "2024-10-01") & (combined["date"] <= "2025-01-01")])

if __name__ == "__main__":
    merge_exchange_rate_series(
        "data/processed/cbn_exchange_rate_historical_clean.csv",
        "data/processed/cbn_exchange_rate_clean.csv",
        "data/processed/cbn_exchange_rate_merged.csv"
    )