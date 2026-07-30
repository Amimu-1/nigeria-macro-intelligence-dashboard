import pandas as pd
from pathlib import Path

def inspect_file(filepath: str, sheet_name=0):
    """
    Diagnostic tool: prints raw structure of a downloaded CBN/NBS file
    so we know exactly how to clean it before writing the real parser.
    """
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return

    print(f"\n{'='*60}")
    print(f"INSPECTING: {path.name}")
    print(f"{'='*60}")

    raw = pd.read_excel(path, sheet_name=sheet_name, header=None, engine="calamine")

    print(f"\nShape: {raw.shape}")
    print(f"\nFirst 15 rows (raw, no header applied):")
    print(raw.head(15).to_string())

if __name__ == "__main__":
    inspect_file("data/raw/nbs_cpi/nbs_cpi_raw.xlsx")
    inspect_file("data/raw/cbn_inflation/cbn_inflation_raw.xlsx")