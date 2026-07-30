import pandas as pd
from pathlib import Path

def clean_cbn_inflation(raw_path: str, output_path: str):
    """
    Cleans the CBN inflation export into a tidy monthly time series.
    Raw file has: tyear, tmonth, period, allItemsYearOn, allItemsAverage,
    foodYearOn, foodAverage, allItemsLessFrmProdYearOn, allItemsLessFrmProdAverage,
    allItemsLessFrmProdAndEnergyYearOn, allItemsLessFrmProdAndEnergyAvg
    """
    df = pd.read_excel(raw_path, engine="calamine")

    # Build a proper date column from tyear + tmonth
    df["date"] = pd.to_datetime(
        df["tyear"].astype(str) + "-" + df["tmonth"].astype(str) + "-01",
        format="%Y-%m-%d"
    )

    # Rename to clear, analysis-friendly column names
    df = df.rename(columns={
        "allItemsYearOn": "headline_inflation_yoy",
        "allItemsAverage": "headline_inflation_avg",
        "foodYearOn": "food_inflation_yoy",
        "foodAverage": "food_inflation_avg",
        "allItemsLessFrmProdYearOn": "core_inflation_yoy",
        "allItemsLessFrmProdAverage": "core_inflation_avg",
        "allItemsLessFrmProdAndEnergyYearOn": "core_ex_energy_yoy",
        "allItemsLessFrmProdAndEnergyAvg": "core_ex_energy_avg",
    })

    # Keep only what we need, sorted chronologically
    keep_cols = ["date", "headline_inflation_yoy", "headline_inflation_avg",
                 "food_inflation_yoy", "food_inflation_avg",
                 "core_inflation_yoy", "core_inflation_avg",
                 "core_ex_energy_yoy", "core_ex_energy_avg"]
    df = df[keep_cols].sort_values("date").reset_index(drop=True)

    # Filter to our project window: 2015-01 to 2025-12
    df = df[(df["date"] >= "2015-01-01") & (df["date"] <= "2025-12-31")]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Cleaned CBN inflation data saved to {output_path}")
    print(f"Rows: {len(df)}, Date range: {df['date'].min()} to {df['date'].max()}")
    print(df.head())
    print(df.tail())

if __name__ == "__main__":
    clean_cbn_inflation(
        "data/raw/cbn_inflation/cbn_inflation_raw.xlsx",
        "data/processed/cbn_inflation_clean.csv"
    )