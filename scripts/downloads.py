import cryptohftdata as chd
from pathlib import Path
import gc

def download_cryptohft_by_day():
    target_dir = Path("data") / "historical" / "BTCUSDT"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print("[*] Connecting to CryptoHFTData API...")
    # Replace with your actual dashboard API key
    client = chd.CryptoHFTDataClient(api_key="e2ec67ffdca85f0a86a81791b37024478c3a7cef3b81a3f2557f38d709b1d699") 
    
    # Process day-by-day to keep memory footprint low
    target_dates = [
        "2026-05-01",
        "2026-05-02",
        "2026-05-03",
        "2026-05-04",
        "2026-05-05",
        "2026-05-06",
        "2026-05-07"
    ]
    
    for current_date in target_dates:
        print(f"\n=== Processing Date: {current_date} ===")
        
        # 1. Handle Order Book Data
        ob_path = target_dir / f"BTCUSDT_orderbook_{current_date}.parquet"
        if not ob_path.exists():
            print(f"  [*] Fetching L2 Order Book for {current_date}...")
            try:
                orderbook_df = client.get_orderbook(
                    symbol="BTCUSDT",
                    exchange=chd.exchanges.BINANCE_FUTURES,
                    start_date=current_date,
                    end_date=current_date
                )
                orderbook_df.to_parquet(ob_path)
                print(f"  [SUCCESS] Order book saved to {ob_path.name}")
                
                # Force garbage collection to free up memory immediately
                del orderbook_df
                gc.collect()
            except Exception as e:
                print(f"  [ERROR] Failed downloading orderbook for {current_date}: {e}")
        else:
            print(f"  [-] Order book for {current_date} already exists on disk. Skipping.")

        # 2. Handle Trades Data
        trades_path = target_dir / f"BTCUSDT_trades_{current_date}.parquet"
        if not trades_path.exists():
            print(f"  [*] Fetching Trades for {current_date}...")
            try:
                trades_df = client.get_trades(
                    symbol="BTCUSDT",
                    exchange=chd.exchanges.BINANCE_FUTURES,
                    start_date=current_date,
                    end_date=current_date
                )
                trades_df.to_parquet(trades_path)
                print(f"  [SUCCESS] Trades saved to {trades_path.name}")
                
                del trades_df
                gc.collect()
            except Exception as e:
                print(f"  [ERROR] Failed downloading trades for {current_date}: {e}")
        else:
            print(f"  [-] Trades for {current_date} already exists on disk. Skipping.")

    print("\n[SUCCESS] Pipeline completed! All data stored safely as daily chunks.")

if __name__ == "__main__":
    download_cryptohft_by_day()