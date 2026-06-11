import polars as pl
from pathlib import Path
import gc

def _process_single_lazy_file(file_path: Path, save_path: Path):
    """Internal helper: Processes a single Parquet file lazily."""
    print(f"    -> Processing (Lazy Stream): {file_path.name}")
    
    lf = pl.scan_parquet(file_path)
    
    lf = lf.with_columns([
        pl.col("price").cast(pl.Float64),
        pl.col("quantity").cast(pl.Float64)
    ])
    
    bids = lf.filter(pl.col("side") == "bid")
    asks = lf.filter(pl.col("side") == "ask")
    
    best_bids = (bids.sort(["transaction_time", "price"], descending=[False, True])
                     .group_by("transaction_time", maintain_order=True)
                     .first()
                     .select([
                         "transaction_time", 
                         pl.col("price").alias("best_bid_price"), 
                         pl.col("quantity").alias("best_bid_qty")
                     ]))
                     
    best_asks = (asks.sort(["transaction_time", "price"], descending=[False, False])
                     .group_by("transaction_time", maintain_order=True)
                     .first()
                     .select([
                         "transaction_time", 
                         pl.col("price").alias("best_ask_price"), 
                         pl.col("quantity").alias("best_ask_qty")
                     ]))
                     
    l1_book = best_bids.join(best_asks, on="transaction_time", how="inner")
    
    l1_book = l1_book.with_columns([
        (pl.col("best_ask_price") - pl.col("best_bid_price")).alias("spread"),
        ((pl.col("best_bid_qty") - pl.col("best_ask_qty")) / 
         (pl.col("best_bid_qty") + pl.col("best_ask_qty"))).alias("obi")
    ])
    
    df_final = l1_book.collect(streaming=True)
    df_final.write_parquet(save_path)
    print(f"    [SAVED] {save_path.name}")

def preprocess_all_orderbooks(data_dir: str | Path = None):
    """
    CLI entry point: Loops through all raw orderbook files and triggers the lazy processor.
    """
    if data_dir is None:
        data_dir = Path("data") / "historical" / "BTCUSDT" / "preprocessed"
    else:
        data_dir = Path(data_dir)
        
    parquet_files = sorted(list(data_dir.glob("*_orderbook_*.parquet")))
    
    if not parquet_files:
        print("[ERROR] No raw Parquet files found. Check your data directory.")
        return

    print(f"\n[*] Found {len(parquet_files)} days of data to process lazily.")
    
    for file_path in parquet_files:
        date_str = file_path.stem.split("_")[-1]
        save_path = data_dir / f"BTCUSDT_features_{date_str}.parquet"
        
        if save_path.exists():
            print(f"[-] Skipping {date_str} - Features already exist.")
            continue
            
        _process_single_lazy_file(file_path, save_path)
        gc.collect()
        
    print("\n[SUCCESS] Pipeline completed successfully.")