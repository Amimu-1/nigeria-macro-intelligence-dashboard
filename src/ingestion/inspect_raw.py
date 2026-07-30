import pandas as pd
from pathlib import Path

def list_sheet_names(filepath: str):
    """Lists all sheet names in a multi-sheet workbook."""
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return
    xl = pd.ExcelFile(path, engine="calamine")
    print(f"\n{'='*60}")
    print(f"SHEETS IN: {path.name}")
    print(f"{'='*60}")
    for i, sheet in enumerate(xl.sheet_names):
        print(f"{i}: {sheet}")

def inspect_file(filepath: str, sheet_name=0):
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return
    print(f"\n{'='*60}")
    print(f"INSPECTING: {path.name} (sheet: {sheet_name})")
    print(f"{'='*60}")
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None, engine="calamine")
    print(f"\nShape: {raw.shape}")
    print(f"\nFirst 15 rows (raw, no header applied):")
    print(raw.to_string())
if __name__ == "__main__":
    inspect_file("data/raw/cbn_exchange_rate/statistical_bulletin_financial_sector.xlsx", sheet_name=34)