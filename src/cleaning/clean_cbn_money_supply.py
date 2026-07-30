import pandas as pd
from pathlib import Path

def clean_cbn_money_supply(raw_path: str, output_path: str):
    """
    Cleans CBN Statistical Bulletin A1.2 (Depository Corporations Survey).
    Extracts the 'BROAD MONEY LIABILITIES' row (M2 equivalent), reported
    annually (year-end December figure) in Naira Billion.

    Note: 2023 and 2024 columns are split into quarters (March, June,
    September, December) rather than one annual column. We take the
    December (year-end) column for each of those years explicitly.
    """
    raw = pd.read_excel(raw_path, sheet_name="A1.2", header=None, engine="calamine")

    year_row = raw.iloc[2, 1:25]
    broad_money_row = raw.iloc[56, 1:25]

    data = pd.DataFrame({
        "year_raw": year_row.values,
        "broad_money": broad_money_row.values
    })
    data["broad_money"] = pd.to_numeric(data["broad_money"], errors="coerce")

    # Clean annual columns (2007-2022): straightforward numeric year headers
    data["year"] = pd.to_numeric(data["year_raw"], errors="coerce")
    clean_years = data.dropna(subset=["year"]).copy()
    clean_years["year"] = clean_years["year"].astype(int)
    clean_years = clean_years[["year", "broad_money"]]

    # 2023 and 2024 year-end (December) values sit at fixed positions
    # within the 1:25 slice: index 19 = 2023 Dec, index 23 = 2024 Dec
    # (i.e. raw column 20 and 24 respectively)
    dec_2023 = raw.iloc[56, 20]
    dec_2024 = raw.iloc[56, 24]

    extra_years = pd.DataFrame({
        "year": [2023, 2024],
        "broad_money": [pd.to_numeric(dec_2023), pd.to_numeric(dec_2024)]
    })

    combined = pd.concat([clean_years, extra_years], ignore_index=True)
    combined = combined.dropna(subset=["broad_money"])
    combined = combined[(combined["year"] >= 2015) & (combined["year"] <= 2025)]

    combined["date"] = pd.to_datetime(combined["year"].astype(str) + "-12-01")
    combined = combined[["date", "broad_money"]].sort_values("date").reset_index(drop=True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_path, index=False)

    print(f"Cleaned money supply data saved to {output_path}")
    print(f"Rows: {len(combined)}, Date range: {combined['date'].min()} to {combined['date'].max()}")
    print(combined)

if __name__ == "__main__":
    clean_cbn_money_supply(
        "data/raw/cbn_exchange_rate/statistical_bulletin_financial_sector.xlsx",
        "data/processed/cbn_money_supply_clean.csv"
    )