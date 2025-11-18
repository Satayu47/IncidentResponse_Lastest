# Contributing to Incident Response ChatOps Assistant

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up API keys in `.env` file
4. Run tests: `pytest tests/ -v`

## Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions and classes

## Testing

- All new features should include tests
- Run full test suite before submitting: `pytest tests/ -v`
- Accuracy tests: `python tests/accuracy/test_accuracy_50_cases.py`

## Pull Requests

1. Create a feature branch
2. Make your changes
3. Ensure all tests pass
4. Update documentation if needed
5. Submit PR with clear description

## API Keys

**Never commit API keys!** All keys should be in `.env` file (which is gitignored).

