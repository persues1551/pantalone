# Pantalone

AI-powered A-stock (China) investment research system. Named after the merchant character in Commedia dell'arte.

Pantalone is a Hermes Skill for evidence-based investment research. It ships the OCIFQ methodology, an eight-stage workflow, role prompts, rules, templates and portable helper scripts. Data, machine-learning and production-state capabilities are optional host integrations and must be probed before use.

## Key Features

- OCIFQ stock picking framework (5 dimensions: Oligopoly, Catalyst, Industry profit gap, Financial triple-breakout, Quarterly consistency)
- Eight-stage deep-research contract with independent risk, compliance and final review stages
- A+/A/B/C observation-pool contract; recommendations are read-only by default and every state change requires explicit authorization
- ETF, market, capital-flow, financial, macro, theme, technical and risk research roles
- Optional host data, sentiment, ML, backtest and document-generation capabilities with fail-closed fallbacks
- Portable report templates, capability probes and integration-contract tests

## Architecture

```
SOUL.md (philosophy & principles)
  └── router.md (task routing)
      └── workflow_v4_unified.md (authoritative execution contract)
          ├── subagents/ (specialist and supporting role contracts)
          ├── rules/ (authoritative investment and authorization rules)
          └── templates/ (15 active report and review templates)
```

## Requirements

- Hermes Agent with the file, web/search, delegation and terminal capabilities required by the selected workflow
- Python 3.10+ for the optional helper scripts shipped in `scripts/`
- External data and ML capabilities are optional and declared in `references/external-capabilities.yaml`

## Installation

Install or clone this repository as the `pantalone` Hermes Skill, then load it with `/skill pantalone` or `hermes -s pantalone`. Python dependencies in `requirements.txt` are only needed when running helper or host capabilities that import them; installing those dependencies does not create a standalone Pantalone CLI.

## Data Sources

| Source | Coverage | Rate Limit |
|--------|----------|------------|
| Sina Finance API | Real-time quotes, market overview | None |
| Tencent Quote API | Real-time quotes, technical indicators | None |
| AKShare | ETF, sectors, financials | Heavy (429) |
| Tushare Pro | Northbound flow, SHIBOR, daily bars | 120-credit tier |
| yfinance | Fundamentals (PE/PB/ROE), US stocks | Moderate (429) |
| East Money | News, sector flow, LHB, margin trading | IP-based throttling |

## Optional ML Evidence

This repository does not ship a trained model artifact or claim that a model is deployed. ML prediction, backtest and training are optional host capabilities declared in `references/external-capabilities.yaml`. Use ML output only after verifying the script and artifact exist and recording the model version, training window, validation method, data source and `as_of` time. If any requirement is missing, keep ML fields unknown and do not apply an ML score or weight.

## Usage

Start a Hermes conversation with the Skill loaded and ask for a market review, stock/ETF analysis, or full research task. Requests containing “研究”“研究一下” or “深入分析” follow the eight-stage contract in `workflow_v4_unified.md`.

ML prediction, OCIFQ automation, sentiment, observation-pool and training scripts are optional host capabilities. Their expected `$HERMES_HOME` paths and fallbacks are defined in `references/external-capabilities.yaml`; check availability before invoking them and never report a missing script as executed.

### Observation Pool Review

```bash
# Read-only scan/report examples. External scripts are optional and must be
# probed under $HERMES_HOME before use.
python3 $HERMES_HOME/scripts/amadeus/pool_manager.py scan
python3 $HERMES_HOME/scripts/amadeus/pool_manager.py report
```

Pool changes are advisory by default. Any add/remove/apply/auto operation
requires explicit user authorization for that action.

### Local Verification

```bash
python3 scripts/check_references_health.py --quiet
python3 -m pytest -q tests/test_integration_contract.py
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
├── references/           # Technical documentation and capability manifest
└── scripts/              # Portable helper and verification scripts
```

### Scripts

| Script | Purpose |
|--------|---------|
| `amadeus_sim_integrate.py` | Read and summarize optional simulation state |
| `check_references_health.py` | Check references, routing and release-tree hygiene |
| `md2docx.py` | Convert Markdown reports to DOCX |
| `probe_external_capabilities.py` | Probe optional host capabilities with fail-closed fallbacks |
| `tencent_quote_parser.py` | Parse Tencent quote responses |
| `token_audit.py` | Audit active documentation size |

Other scripts mentioned by the workflow are external Hermes host capabilities, not files shipped by this repository.

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
| M - Optional ML evidence | Runtime-dependent | Use only after the host capability and model provenance are verified; otherwise unknown |

The OCIFQ dimensions are the local research contract. Optional ML evidence does not receive a fixed weight merely because an external script or historical result exists.

## Research Signal Boundaries

- OCIFQ and any verified optional ML output are research evidence, not trade instructions.
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
