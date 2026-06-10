"""CLI entry point: download historical order book and trade data."""

from rl_arbitrage.download import download_cryptohft_by_day

if __name__ == "__main__":
    download_cryptohft_by_day()
