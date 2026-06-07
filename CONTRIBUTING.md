# Contributing to Pantalone

Thank you for your interest in contributing to Pantalone!

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or suggest features
- Include steps to reproduce for bug reports
- Include your Python version and OS

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run the QA loop to verify: `python3 scripts/qa_loop.py --data-only`
5. Commit with clear messages
6. Open a Pull Request

### Code Style

- Python 3.10+ compatible
- Use type hints where practical
- Follow PEP 8
- All data scripts must use `data_validator.py` for validation
- New data sources must implement fallback chains

### Adding New Data Sources

1. Add the source function in the appropriate script
2. Register it in `data_source_manager.py` with priority and fallback
3. Add validation in `data_validator.py`
4. Update the data quality assessment in `data_quality.py`
5. Test with `qa_loop.py`

### Adding New ML Features

1. Add feature extraction in the training script
2. Retrain with TimeSeriesSplit (never use full-data AUC)
3. Compare CV AUC against current best (v5.1: 0.6512)
4. Document feature importance and rationale

### Security

Never commit:
- API tokens or keys
- Personal cache files
- Session state files
- Hardcoded credentials

Use environment variables or config files excluded by `.gitignore`.

## Code of Conduct

Be respectful, constructive, and focus on what is best for the community.
