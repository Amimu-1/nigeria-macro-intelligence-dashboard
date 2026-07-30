import pandas as pd
from pathlib import Path

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

def clean_historical_exchange_rate(raw_path: str, output_path: str):
    """
    Cleans the CBN Statistical Bulletin D.4.1 sheet (wide format: years as rows,
    months as columns) into a tidy monthly time series, then merges with the
    Dec 2024-present NFEM data to produce one continuous series.
    """
    raw = pd.read_excel(raw_path, sheet_name="D.4.1", header=None, engine="calamine")

    # Data rows are 3 to 46 (years 1981-2024), columns 0=year, 1-12=months, 13=average
    data = raw.iloc[3:47].copy()
    data.columns = ["year"] + list(MONTH_MAP.keys()) + ["annual_average"]

    # Melt months into rows
    long_df = data.melt(id_vars=["year"], value_vars=list(MONTH_MAP.keys()),
                         var_name="month_name", value_name="official_rate")

    long_df["month"] = long_df["month_name"].map(MONTH_MAP)
    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce")
    long_df["official_rate"] = pd.to_numeric(long_df["official_rate"], errors="coerce")
    long_df = long_df.dropna(subset=["year", "official_rate"])

    long_df["date"] = pd.to_datetime(
        long_df["year"].astype(int).astype(str) + "-" + long_df["month"].astype(int).astype(str) + "-01"
    )
    long_df = long_df[["date", "official_rate"]].sort_values("date").reset_index(drop=True)

    # Filter to our project window start (2015-01), and stop before Dec 2024
    # since NFEM data takes over from there
    long_df = long_df[(long_df["date"] >= "2015-01-01") & (long_df["date"] < "2024-12-01")]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    long_df.to_csv(output_path, index=False)

    print(f"Cleaned historical exchange rate data saved to {output_path}")
    print(f"Rows: {len(long_df)}, Date range: {long_df['date'].min()} to {long_df['date'].max()}")
    print(long_df.head())
    print(long_df.tail())

if __name__ == "__main__":
    clean_historical_exchange_rate(
        "data/raw/cbn_exchange_rate/statistical_bulletin_external_sector.xlsx",
        "data/processed/cbn_exchange_rate_historical_clean.csv"
    )