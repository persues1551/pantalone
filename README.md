# Pantalone

AI-powered A-stock (China) investment research system. Named after the merchant character in Commedia dell'arte.

Pantalone is a modular agent-based system that combines fundamental analysis (OCIFQ framework) with machine learning (LightGBM + XGBoost) to support investment research on China's A-share market.

## Key Features

- OCIFQ stock picking framework (5 dimensions: Oligopoly, Catalyst, Industry profit gap, Financial triple-breakout, Quarterly consistency)
- ML ensemble model (LightGBM + XGBoost, AUC 0.6512, 727 stocks, 606K samples, 66 features)
- Six-dimensional scoring: OCIFQ (70%) + ML signal (30%)
- Sentiment temperature system (market-wide emotion quantification)
- Automated observation pool management (A/B/C tier pools with differentiated stop-loss)
- ETF analysis with 9-category classification and A-E rating
- Multi-source data pipeline with automatic fallback (Sina → Tencent → AKShare → Tushare)
- Subagent architecture for parallel data collection and analysis
- Report generation with humanizer (anti-AI-detection for Chinese text)
- QA closed-loop testing system

## Architecture

```
SOUL.md (philosophy & principles)
  └── router.md (task routing)
      └── workflow_v4_unified.md (authoritative execution contract)
          └── subagents/ (7 parallel agents)
          │   ├── market_data.md
          │   ├── capital.md
          │   ├── macro.md
          │   ├── theme.md
          │   ├── financial.md
          │   ├── technical.md
          │   └── risk.md
          └── rules/ (9 rule files)
              └── templates/ (6 report templates)
```

## Requirements

- Python 3.10+
- Dependencies: akshare, yfinance, tushare, lightgbm, xgboost, scikit-learn, pandas, numpy, requests, beautifulsoup4, python-docx, chromadb, sentence-transformers

## Quick Install

```bash
pip install -r requirements.txt
```

## Data Sources

| Source | Coverage | Rate Limit |
|--------|----------|------------|
| Sina Finance API | Real-time quotes, market overview | None |
| Tencent Quote API | Real-time quotes, technical indicators | None |
| AKShare | ETF, sectors, financials | Heavy (429) |
| Tushare Pro | Northbound flow, SHIBOR, daily bars | 120-credit tier |
| yfinance | Fundamentals (PE/PB/ROE), US stocks | Moderate (429) |
| East Money | News, sector flow, LHB, margin trading | IP-based throttling |

## ML Models

| Version | Stocks | Samples | Features | CV AUC | Status |
|---------|--------|---------|----------|--------|--------|
| v5.1 (prod) | 727 | 606K | 66 | 0.6512 | Current best |
| v4.7 | 733 | 556K | 38 | 0.6499 | Backup |
| v3.5 | 99 | 76K | 41 | ~~0.7785~~ | Data leakage |

Training config: n_estimators=500, lr=0.03, max_depth=7, StandardScaler, TimeSeriesSplit 5-fold.

## Usage

### ML Prediction

```bash
# Single stock
python3 scripts/ml_predict.py --stock 600519

# Multiple stocks with report
python3 scripts/ml_predict.py --stocks 600519,000858,300750 --report

# Full observation pool
python3 scripts/ml_predict.py --pool
```

### OCIFQ + ML Combined Scoring

```bash
python3 scripts/ocifq_ml_selector.py --stocks 600519,000858
```

### Sentiment Temperature

```bash
python3 scripts/amadeus_emotion.py
```

### Observation Pool Review

```bash
# Read-only scan/report examples. External scripts are optional and must be
# probed under $HERMES_HOME before use.
python3 $HERMES_HOME/scripts/amadeus/pool_manager.py scan
python3 $HERMES_HOME/scripts/amadeus/pool_manager.py report
```

Pool changes are advisory by default. Any add/remove/apply/auto operation
requires explicit user authorization for that action.

### Data Quality Check

```bash
python3 scripts/data_quality.py --report-fragment
```

### QA Loop

```bash
# Full closed-loop test
python3 scripts/qa_loop.py

# Format-only (no network)
python3 scripts/qa_loop.py --data-only
```

## Project Structure

```
pantalone/
├── SKILL.md              # Main documentation (entry point)
├── SOUL.md               # Investment philosophy & principles
├── router.md             # Task routing logic
├── workflow_v4_unified.md # Authoritative execution contract
├── subagents/            # Parallel agent definitions
│   ├── market_data.md
│   ├── capital.md
│   ├── financial.md
│   ├── risk.md
│   ├── theme.md
│   └── research.md
├── rules/                # Business rules
├── templates/            # Report templates
├── references/           # Technical documentation (50+ files)
└── scripts/              # Python scripts (see below)
```

### Scripts

| Script | Purpose |
|--------|---------|
| `ml_predict.py` | ML ensemble prediction (LightGBM + XGBoost) |
| `ocifq_ml_selector.py` | OCIFQ + ML six-dimensional scoring |
| `amadeus_emotion.py` | Sentiment temperature calculation |
| `amadeus_pool_manager.py` | Observation pool management |
| `amadeus_data.py` | Market data collection (multi-source) |
| `amadeus_realtime.py` | Real-time quotes + technical indicators |
| `amadeus_financials.py` | Financial statement analysis |
| `amadeus_news_scanner.py` | News scanning (4 sources) |
| `amadeus_sector_flow.py` | Sector capital flow |
| `amadeus_external.py` | US/HK markets, forex, futures |
| `amadeus_indicators.py` | Technical indicators (MA/MACD/RSI/Bollinger) |
| `amadeus_screening.py` | Risk screening |
| `amadeus_etf_pool_manager.py` | ETF pool management |
| `amadeus_sim_integrate.py` | Simulation engine |
| `data_source_manager.py` | Multi-source data manager with fallback |
| `data_validator.py` | Data validation utilities |
| `data_quality.py` | Data quality assessment |
| `ml_simulation.py` | Simulated trading |
| `ml_backtest.py` | Historical backtesting |
| `train_models.py` | Model training pipeline |
| `factor_miner.py` | Factor mining & validation |
| `pantalone_tools_hub.py` | Unified signal generation hub |
| `humanize_auto.py` | Chinese text anti-AI-detection |
| `to_docx.py` | Markdown to DOCX conversion |
| `qa_loop.py` | QA closed-loop testing |

## OCIFQ Framework

The core stock-picking methodology:

**Industry Money Machine = O x C x I x F x Q**

| Dimension | Weight | Description |
|-----------|--------|-------------|
| O - Oligopoly Pricing Power | 15% | CR3 concentration, patent barriers, switching costs, gross margin >= 30% |
| C - Long-cycle Catalyst | 12% | Catalysts lasting >= 4 quarters (AI, energy, tech iteration, policy) |
| I - Industry Profit Gap | 12% | Multiple companies in same industry showing synchronized improvement |
| F - Financial Triple Breakout | 20% | Revenue >= 30% YoY + Net profit >= 50% YoY + Gross margin >= 5ppt |
| Q - Quarterly Consistency | 9% | 4 consecutive quarters of improving revenue/profit/margin |
| M - ML Signal | 30% | LightGBM + XGBoost ensemble score |

Hard gates: Missing any of F's three criteria caps at grade B. F < 70 caps total at 75. ML < 30 caps at 65.

## Research Signal Boundaries

- OCIFQ and ML scores are research evidence, not trade instructions.
- Stock stop-loss rules come only from the A+/A/B/C contract in `rules/pool_rules.md`.
- Stock take-profit rules come only from the +12%/+20%/+30% contract in `rules/risk_rules.md`.
- Technical indicators and holding periods cannot independently trigger stock actions.
- A single stock may not exceed 25% of capital; the minimum trading lot is not an exception.
- Any simulated or production state change requires explicit authorization for that action.

## Disclaimer

This project is for educational and research purposes only. It does not constitute investment advice. The stock market involves risk. Always do your own due diligence before making investment decisions.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- OCIFQ framework inspired by 川沐 (Xiaohongshu: 5303101410)
- ML pipeline influenced by Qlib (Microsoft)
- Agent architecture inspired by Commedia dell'arte
- Named after Wolfgang Amadeus Mozart
