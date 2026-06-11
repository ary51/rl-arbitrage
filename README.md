# rl-arbitrage

A dual-engine infrastructure for reinforcement learning-based arbitrage research on cryptocurrency market microstructure.

This repository is split into two distinct operational environments:
1. **The Research Pipeline (Python):** A Polars-driven data engineering pipeline to process historical L2 order book delta streams into continuous ML features (Spread, OBI) for neural network training.
2. **The Execution Engine (C++):** A native, zero-latency WebSocket ingestion engine designed to manage live order book state via Red-Black Trees (std::map) directly from the Binance matching engine.

## Project layout

```
rl-arbitrage/
├── include/              # C++ headers (OrderBook state management)
├── src/
│   ├── cpp/              # C++ source code (WebSocket loop)
│   └── rl_arbitrage/     # Python library (Data engineering pipeline)
├── scripts/              # Python CLI entry points
├── tests/
├── data/                 # Downloaded Parquet files (gitignored)
├── build/                # CMake build output (gitignored)
├── pyproject.toml
└── CMakeLists.txt
```

## Python Data Pipeline

The Python pipeline utilizes Polars LazyFrames to process massive tick-level data without memory bottlenecks.

### Setup
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and set your CryptoHFTData API key:

```
CRYPTOHFTDATA_API_KEY=your_key_here
```

### Usage

Run scripts from the project root:

Run the following scripts from the project root sequentially:
1. `python scripts/download_data.py` - Fetches historical data.
2. `python scripts/verify_data.py` - Validates timestamp integrity and uncrossed spreads.
3. `python scripts/preprocess_data.py` - Compiles the lazy execution graph and exports final Parquet features.

## C++ Live Ingestion Engine

The execution engine connects to the Binance Futures @depth@100ms stream, parsing JSON payloads and continuously sorting the Top of Book (L1) state.

### Dependencies
This project uses `vcpkg` for dependency management. Ensure `vcpkg` is bootstrapped on your system.
* ixwebsocket
* nlohmann-json

### Compilation (Windows MSVC)
Run the following commands from the project root, replacing the toolchain path with your local vcpkg installation:

```
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=[path_to_vcpkg]/scripts/buildsystems/vcpkg.cmake -DVCPKG_TARGET_TRIPLET=x64-windows
cmake --build build --config Release
```

### Execution
```
.\build\Release\IngestionEngine.exe
```