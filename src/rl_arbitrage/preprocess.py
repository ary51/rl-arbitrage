import gc
from pathlib import Path

import polars as pl

from rl_arbitrage.config import DATA_DIR, SYMBOL


def build_order_book_features(file_path: Path) -> pl.DataFrame:
    print(f"\n[*] Processing {file_path.name}...")

    df = pl.read_parquet(file_path)

    df = df.with_columns([
        pl.col("price").cast(pl.Float64),
        pl.col("quantity").cast(pl.Float64),
    ])

    print("    -> Reconstructing Top of Book (L1) from event stream...")

    bids = df.filter(pl.col("side") == "bid")
    asks = df.filter(pl.col("side") == "ask")

    best_bids = (
        bids.sort(["transaction_time", "price"], descending=[False, True])
        .group_by("transaction_time", maintain_order=True)
        .first()
        .select([
            "transaction_time",
            pl.col("price").alias("best_bid_price"),
            pl.col("quantity").alias("best_bid_qty"),
        ])
    )

    best_asks = (
        asks.sort(["transaction_time", "price"], descending=[False, False])
        .group_by("transaction_time", maintain_order=True)
        .first()
        .select([
            "transaction_time",
            pl.col("price").alias("best_ask_price"),
            pl.col("quantity").alias("best_ask_qty"),
        ])
    )

    print("    -> Calculating Spread and Imbalance...")

    l1_book = best_bids.join(best_asks, on="transaction_time", how="inner")

    l1_book = l1_book.with_columns([
        (pl.col("best_ask_price") - pl.col("best_bid_price")).alias("spread"),
        (
            (pl.col("best_bid_qty") - pl.col("best_ask_qty"))
            / (pl.col("best_bid_qty") + pl.col("best_ask_qty"))
        ).alias("obi"),
    ])

    return l1_book


def preprocess_all_orderbooks(data_dir: Path = DATA_DIR) -> None:
    parquet_files = sorted(data_dir.glob(f"{SYMBOL}_orderbook_*.parquet"))

    if not parquet_files:
        print("[ERROR] No Parquet files found. Check your data directory.")
        return

    print(f"[*] Found {len(parquet_files)} days of data to process.")

    for file_path in parquet_files:
        date_str = file_path.stem.split("_")[-1]
        df_features = build_order_book_features(file_path)

        save_path = data_dir / f"{SYMBOL}_features_{date_str}.parquet"
        df_features.write_parquet(save_path)

        print(f"    [SAVED] Ready for PyTorch! File written to: {save_path.name}")

        del df_features
        gc.collect()

    print(f"\n[SUCCESS] All {len(parquet_files)} days have been processed and saved!")
