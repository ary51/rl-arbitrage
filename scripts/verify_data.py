"""CLI entry point: inspect downloaded Parquet files."""

from pathlib import Path

from rl_arbitrage.verify import verify_orderbook_lazy

if __name__ == "__main__":
    target_file = Path("data/historical/BTCUSDT/BTCUSDT_orderbook_2026-05-01.parquet")
    if target_file.exists():
        verify_orderbook_lazy(target_file)
    else:
        print(f"Data file not found at {target_file}. Please check the path.")
