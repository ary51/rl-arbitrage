"""CLI entry point: build L1 features from raw order book data."""

from rl_arbitrage.preprocess import preprocess_all_orderbooks

if __name__ == "__main__":
    preprocess_all_orderbooks()
