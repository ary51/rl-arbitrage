import polars as pl
from pathlib import Path
import gc

def build_order_book_features(file_path: Path):
    print(f"\n[*] Processing {file_path.name}...")
    
    # Read the Parquet file
    df = pl.read_parquet(file_path)
    
    # 1. Cast string values to floats so we can do math on them
    df = df.with_columns([
        pl.col("price").cast(pl.Float64),
        pl.col("quantity").cast(pl.Float64)
    ])
    
    print("    -> Reconstructing Top of Book (L1) from event stream...")
    
    # 2. Separate the stream into Bids and Asks
    bids = df.filter(pl.col("side") == "bid")
    asks = df.filter(pl.col("side") == "ask")
    
    # 3. Find the Best Bid (Highest Price) per timestamp
    best_bids = (bids.sort(["transaction_time", "price"], descending=[False, True])
                     .group_by("transaction_time", maintain_order=True)
                     .first()
                     .select([
                         "transaction_time", 
                         pl.col("price").alias("best_bid_price"), 
                         pl.col("quantity").alias("best_bid_qty")
                     ]))
                     
    # 4. Find the Best Ask (Lowest Price) per timestamp
    best_asks = (asks.sort(["transaction_time", "price"], descending=[False, False])
                     .group_by("transaction_time", maintain_order=True)
                     .first()
                     .select([
                         "transaction_time", 
                         pl.col("price").alias("best_ask_price"), 
                         pl.col("quantity").alias("best_ask_qty")
                     ]))
                     
    print("    -> Calculating Spread and Imbalance...")
    
    # 5. Join them together horizontally where the timestamps match exactly
    l1_book = best_bids.join(best_asks, on="transaction_time", how="inner")
    
    # 6. Calculate the final ML features
    l1_book = l1_book.with_columns([
        (pl.col("best_ask_price") - pl.col("best_bid_price")).alias("spread"),
        ((pl.col("best_bid_qty") - pl.col("best_ask_qty")) / 
         (pl.col("best_bid_qty") + pl.col("best_ask_qty"))).alias("obi")
    ])
    
    return l1_book

if __name__ == "__main__":
    data_dir = Path("data") / "historical" / "BTCUSDT"
    
    # Grab all 7 orderbook files and sort them chronologically
    parquet_files = sorted(list(data_dir.glob("*_orderbook_*.parquet")))
    
    if parquet_files:
        print(f"[*] Found {len(parquet_files)} days of data to process.")
        
        for file_path in parquet_files:
            # Extract the date string from the filename (e.g., "2026-05-01")
            date_str = file_path.stem.split("_")[-1]
            
            # Process the math
            df_features = build_order_book_features(file_path)
            
            # Save it dynamically to match the day
            save_path = data_dir / f"BTCUSDT_features_{date_str}.parquet"
            df_features.write_parquet(save_path)
            
            print(f"    [SAVED] Ready for PyTorch! File written to: {save_path.name}")
            
            # Wipe RAM before loading the next day
            del df_features
            gc.collect()
            
        print("\n[SUCCESS] All 7 days have been processed and saved!")
    else:
        print("[ERROR] No Parquet files found. Check your data directory.")