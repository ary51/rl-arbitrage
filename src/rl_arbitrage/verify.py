import polars as pl
from pathlib import Path
import time

def verify_orderbook_lazy(file_path: str | Path):
    print(f"Inspecting file: {file_path}")
    start_time = time.time()
    
    # 1. Use SCAN instead of READ. This creates a "LazyFrame" (a query plan) 
    # instead of loading the massive file into memory.
    try:
        lf = pl.scan_parquet(file_path)
    except Exception as e:
        print(f"Failed to scan parquet: {e}")
        return

    # Check for the correct Binance column (requires a quick eager peek at the schema)
    if "transaction_time" not in lf.collect_schema().names():
        print("Error: 'transaction_time' column missing.")
        return
        
    # 2. Build the computational graph (Nothing is actually executed yet)
    lf = lf.with_columns([
        pl.col("price").cast(pl.Float64),
        pl.col("quantity").cast(pl.Float64),
        pl.from_epoch(pl.col("transaction_time"), time_unit="ms").alias("datetime_ms")
    ])
    
    bids = lf.filter(pl.col("side") == "bid").group_by("transaction_time").agg(
        pl.len().alias("bid_depths"),
        pl.col("price").max().alias("best_bid")
    )
    
    asks = lf.filter(pl.col("side") == "ask").group_by("transaction_time").agg(
        pl.len().alias("ask_depths"),
        pl.col("price").min().alias("best_ask")
    )
    
    # Join bids and asks on the exact timestamp
    alignment = bids.join(asks, on="transaction_time", how="inner")
    
    # Validation Checks
    verification = alignment.with_columns([
        (pl.col("bid_depths") == pl.col("ask_depths")).alias("is_aligned"),
        (pl.col("best_bid") < pl.col("best_ask")).alias("valid_spread")
    ])
    
    # We only care about the misaligned data, so we filter it in the lazy graph
    misaligned_query = verification.filter(~pl.col("is_aligned") | ~pl.col("valid_spread"))
    
    print("\nExecuting highly optimized query... (This keeps your RAM safe!)")
    
    # 3. COLLECT triggers the execution. 
    # By using engine="streaming", Polars processes the file in batches.
    misaligned = misaligned_query.collect(engine="streaming")
    
    elapsed_time = time.time() - start_time

    if len(misaligned) == 0:
        print(f"✅ Verification Passed in {elapsed_time:.2f} seconds.")
    else:
        print(f"❌ Verification Failed: Found {len(misaligned)} irregular updates.")
        print(misaligned.head())