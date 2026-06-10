import gc
from pathlib import Path

import cryptohftdata as chd

from rl_arbitrage.config import DATA_DIR, DEFAULT_TARGET_DATES, SYMBOL, get_api_key


def download_cryptohft_by_day(
    target_dir: Path = DATA_DIR,
    target_dates: list[str] | None = None,
    api_key: str | None = None,
) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    dates = target_dates or DEFAULT_TARGET_DATES
    key = api_key or get_api_key()

    print("[*] Connecting to CryptoHFTData API...")
    client = chd.CryptoHFTDataClient(api_key=key)

    for current_date in dates:
        print(f"\n=== Processing Date: {current_date} ===")

        ob_path = target_dir / f"{SYMBOL}_orderbook_{current_date}.parquet"
        if not ob_path.exists():
            print(f"  [*] Fetching L2 Order Book for {current_date}...")
            try:
                orderbook_df = client.get_orderbook(
                    symbol=SYMBOL,
                    exchange=chd.exchanges.BINANCE_FUTURES,
                    start_date=current_date,
                    end_date=current_date,
                )
                orderbook_df.to_parquet(ob_path)
                print(f"  [SUCCESS] Order book saved to {ob_path.name}")

                del orderbook_df
                gc.collect()
            except Exception as e:
                print(f"  [ERROR] Failed downloading orderbook for {current_date}: {e}")
        else:
            print(f"  [-] Order book for {current_date} already exists on disk. Skipping.")

        trades_path = target_dir / f"{SYMBOL}_trades_{current_date}.parquet"
        if not trades_path.exists():
            print(f"  [*] Fetching Trades for {current_date}...")
            try:
                trades_df = client.get_trades(
                    symbol=SYMBOL,
                    exchange=chd.exchanges.BINANCE_FUTURES,
                    start_date=current_date,
                    end_date=current_date,
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
