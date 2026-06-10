import polars as pl
from pathlib import Path

def peek_parquet_file(file_path: Path, num_rows: int = 5):
    """Natively reads a Parquet file's schema and prints the first few rows safely."""
    if not file_path.exists():
        print(f"[ERROR] File {file_path} does not exist.")
        return None
    
    print(f"\n[*] Peeking into: {file_path.name}")
    print("-" * 50)
    
    # 1. Print the schema metadata without loading the data
    # We read exactly 1 row just to capture the column names and data types safely
    meta_df = pl.read_parquet(file_path, n_rows=1)
    print("Schema Layout:")
    for col_name, data_type in meta_df.schema.items():
        print(f"  -> {col_name}: {data_type}")
    
    # 2. Fetch only the requested number of head rows from disk
    df_head = pl.read_parquet(file_path, n_rows=num_rows)
    print(f"\nFirst {num_rows} Rows:")
    print(df_head)
    
    return df_head

if __name__ == "__main__":
    # Configure paths using pathlib to keep things cross-platform
    data_dir = Path("data") / "historical" / "BTCUSDT"

    # Grab the new daily Parquet files available in the directory
    orderbook_files = sorted(list(data_dir.glob("BTCUSDT_orderbook_*.parquet")))
    trade_files = sorted(list(data_dir.glob("BTCUSDT_trades_*.parquet")))

    if orderbook_files and trade_files:
        print("=== STEP 1: VALIDATING L2 ORDER BOOK CHUNK ===")
        peek_parquet_file(orderbook_files[0], num_rows=5)
        
        print("\n=== STEP 2: VALIDATING RAW TRADES CHUNK ===")
        peek_parquet_file(trade_files[0], num_rows=5)
    else:
        print("[ERROR] No daily Parquet files found in the directory.")
        print(f"Please check that files exist inside: {data_dir.resolve()}")