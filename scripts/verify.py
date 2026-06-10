import polars as pl
from pathlib import Path

def verify_orderbook(file_path: str | Path):
    print(f"Inspecting file: {file_path}\n")
    
    # 1. Read the Parquet file
    try:
        df = pl.read_parquet(file_path)
    except Exception as e:
        print(f"Failed to read parquet: {e}")
        return

    # CryptoHFTData SDK standardizes the time column to 'timestamp'
    if "timestamp" not in df.columns:
        print(f"Error: 'timestamp' column missing. Found: {df.columns}")
        return
        
    # 2. Parse Timestamps as Microseconds
    # Convert integer epoch to a datetime object with microsecond precision
    df = df.with_columns(
        pl.from_epoch(pl.col("timestamp"), time_unit="us").alias("datetime_us")
    )
    
    print("--- Sample Parsed Data ---")
    print(df.select(["datetime_us", "side", "level", "price", "size"]).head(5))
    
    # 3. Verify Alignment (Bids vs Asks per timestamp)
    # Group bids and asks independently by the exact microsecond timestamp
    bids = df.filter(pl.col("side") == "bid").group_by("timestamp").agg(
        pl.len().alias("bid_depths"),
        pl.col("price").max().alias("best_bid")
    )
    
    asks = df.filter(pl.col("side") == "ask").group_by("timestamp").agg(
        pl.len().alias("ask_depths"),
        pl.col("price").min().alias("best_ask")
    )
    
    # Join bids and asks on the exact timestamp to check alignment
    alignment = bids.join(asks, on="timestamp", how="inner")
    
    # 4. Validation Checks
    # - is_aligned: Does the number of bid levels exactly match the ask levels?
    # - valid_spread: Is the highest bid strictly lower than the lowest ask (no crossed book)?
    verification = alignment.with_columns(
        (pl.col("bid_depths") == pl.col("ask_depths")).alias("is_aligned"),
        (pl.col("best_bid") < pl.col("best_ask")).alias("valid_spread")
    )
    
    print("\n--- Alignment Check ---")
    print(verification.select([
        "timestamp", "bid_depths", "ask_depths", 
        "best_bid", "best_ask", "is_aligned", "valid_spread"
    ]).head(5))
    
    # Filter for any rows that failed the checks
    misaligned = verification.filter(~pl.col("is_aligned") | ~pl.col("valid_spread"))
    
    if len(misaligned) == 0:
        print("\n✅ Verification Passed: All timestamps are perfectly aligned and no spreads are crossed.")
    else:
        print(f"\n❌ Verification Failed: Found {len(misaligned)} irregular updates.")
        print(misaligned.head())

if __name__ == "__main__":
    # Navigate to your gitignored data folder and pick a sample
    # Example: verify_orderbook("data/BTCUSDT_orderbook_2026-05-01.parquet")
    
    target_file = Path("data") / "historical" / "BTCUSDT" / "BTCUSDT_orderbook_2026-05-01.parquet" # Replace with your actual file name
    if target_file.exists():
        verify_orderbook(target_file)
    else:
        print(f"Data file not found at {target_file}. Please update the path.")