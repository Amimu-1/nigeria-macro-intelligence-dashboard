import pandas as pd
from pathlib import Path

def clean_cbn_exchange_rate(raw_path: str, output_path: str):
    """
    Cleans the CBN NFEM exchange rate export into a tidy daily,
    then aggregated monthly, time series.
    """
    raw = pd.read_excel(raw_path, engine="calamine")

    raw["date"] = pd.to_datetime(raw["ratedate"], format="%B-%d-%Y", errors="coerce")

    raw = raw.rename(columns={
        "closingrate": "closing_rate",
        "highestrate": "highest_rate",
        "lowestrate": "lowest_rate",
        "weightedAvgRate": "nfem_rate",
        "simpleAvgRate": "simple_avg_rate",
    })

    daily = raw[["date", "closing_rate", "highest_rate", "lowest_rate",
                 "nfem_rate", "simple_avg_rate"]].dropna(subset=["date"])
    daily = daily.sort_values("date").reset_index(drop=True)

    print(f"Daily data date range: {daily['date'].min()} to {daily['date'].max()}")
    print(f"Total daily rows: {len(daily)}")

    # Aggregate to monthly average (matches cadence of our other indicators)
    daily["year_month"] = daily["date"].dt.to_period("M")
    monthly = daily.groupby("year_month").agg(
        avg_nfem_rate=("nfem_rate", "mean"),
        avg_closing_rate=("closing_rate", "mean"),
        month_high=("highest_rate", "max"),
        month_low=("lowest_rate", "min"),
    ).reset_index()

    monthly["date"] = monthly["year_month"].dt.to_timestamp()
    monthly = monthly[["date", "avg_nfem_rate", "avg_closing_rate", "month_high", "month_low"]]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(output_path, index=False)

    print(f"\nCleaned monthly exchange rate data saved to {output_path}")
    print(f"Rows: {len(monthly)}, Date range: {monthly['date'].min()} to {monthly['date'].max()}")
    print(monthly.head())
    print(monthly.tail())

if __name__ == "__main__":
    clean_cbn_exchange_rate(
        "data/raw/cbn_exchange_rate/cbn_exchange_rate_raw.xlsx",
        "data/processed/cbn_exchange_rate_clean.csv"
    )