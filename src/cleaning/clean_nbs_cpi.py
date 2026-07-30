import pandas as pd
from pathlib import Path
import re

def clean_nbs_cpi(raw_path: str, output_path: str):
    """
    Cleans the NBS CPI export into a tidy monthly time series.
    Raw file is transposed: rows 0-13 are metadata, data starts at row 14
    with index labels like '2015M1' and two value columns:
    col 1 = Index (2024=100), col 2 = Year-on change (%)
    """
    raw = pd.read_excel(raw_path, engine="calamine", header=None)

    # Data starts at row 14 (0-indexed) based on our inspection
    data = raw.iloc[14:].copy()
    data.columns = ["period_raw", "cpi_index", "inflation_yoy"]

    # Parse period strings like '2015M1' into proper dates
    def parse_period(p):
        match = re.match(r"(\d{4})M(\d{1,2})", str(p))
        if match:
            year, month = match.groups()
            return pd.Timestamp(year=int(year), month=int(month), day=1)
        return pd.NaT

    data["date"] = data["period_raw"].apply(parse_period)
    data = data.dropna(subset=["date"])

    # Convert value columns to numeric (handles any stray text/NaN safely)
    data["cpi_index"] = pd.to_numeric(data["cpi_index"], errors="coerce")
    data["inflation_yoy"] = pd.to_numeric(data["inflation_yoy"], errors="coerce")

    data = data[["date", "cpi_index", "inflation_yoy"]].sort_values("date").reset_index(drop=True)

    # Filter to our project window
    data = data[(data["date"] >= "2015-01-01") & (data["date"] <= "2025-12-31")]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)

    print(f"Cleaned NBS CPI data saved to {output_path}")
    print(f"Rows: {len(data)}, Date range: {data['date'].min()} to {data['date'].max()}")
    print(data.head())
    print(data.tail())

if __name__ == "__main__":
    clean_nbs_cpi(
        "data/raw/nbs_cpi/nbs_cpi_raw.xlsx",
        "data/processed/nbs_cpi_clean.csv"
    )