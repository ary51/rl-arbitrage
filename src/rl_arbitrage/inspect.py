from pathlib import Path

import polars as pl

from rl_arbitrage.config import DATA_DIR, SYMBOL


def peek_parquet_file(file_path: Path, num_rows: int = 5) -> pl.DataFrame | None:
    """Read a Parquet file's schema and print the first few rows."""
    if not file_path.exists():
        print(f"[ERROR] File {file_path} does not exist.")
        return None

    print(f"\n[*] Peeking into: {file_path.name}")
    print("-" * 50)

    meta_df = pl.read_parquet(file_path, n_rows=1)
    print("Schema Layout:")
    for col_name, data_type in meta_df.schema.items():
        print(f"  -> {col_name}: {data_type}")

    df_head = pl.read_parquet(file_path, n_rows=num_rows)
    print(f"\nFirst {num_rows} Rows:")
    print(df_head)

    return df_head


def inspect_sample_data(data_dir: Path = DATA_DIR) -> None:
    orderbook_files = sorted(data_dir.glob(f"{SYMBOL}_orderbook_*.parquet"))
    trade_files = sorted(data_dir.glob(f"{SYMBOL}_trades_*.parquet"))

    if orderbook_files and trade_files:
        print("=== STEP 1: VALIDATING L2 ORDER BOOK CHUNK ===")
        peek_parquet_file(orderbook_files[0], num_rows=5)

        print("\n=== STEP 2: VALIDATING RAW TRADES CHUNK ===")
        peek_parquet_file(trade_files[0], num_rows=5)
    else:
        print("[ERROR] No daily Parquet files found in the directory.")
        print(f"Please check that files exist inside: {data_dir.resolve()}")
