# rl-arbitrage

Data pipeline and feature engineering for RL-based arbitrage research on crypto market microstructure.

## Project layout

```
rl-arbitrage/
├── src/rl_arbitrage/     # importable library code
│   ├── config.py         # paths, constants, env config
│   ├── download.py       # CryptoHFTData download logic
│   ├── preprocess.py     # L1 order book feature engineering
│   └── inspect.py        # Parquet inspection utilities
├── scripts/              # thin CLI entry points
│   ├── download_data.py
│   ├── preprocess_data.py
│   └── inspect_data.py
├── tests/
├── data/                 # downloaded Parquet files (gitignored)
├── pyproject.toml
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and set your CryptoHFTData API key:

```
CRYPTOHFTDATA_API_KEY=your_key_here
```

## Usage

Run scripts from the project root:

```bash
python scripts/download_data.py
python scripts/inspect_data.py
python scripts/preprocess_data.py
```
