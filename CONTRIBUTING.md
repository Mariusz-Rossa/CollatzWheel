# Contributing to CollatzWheel

Thank you for your interest in this project. Contributions are welcome — whether that's bug reports, ideas, or code.

---

## Ways to contribute

- **Bug reports** — open an issue describing what went wrong and how to reproduce it
- **Ideas & discussion** — open an issue with the `discussion` label
- **Code** — fork the repo, make your changes, open a pull request
- **Mathematical insights** — if you spot something interesting in the Wheel × Collatz patterns, open an issue

---

## Development setup

```bash
git clone https://github.com/Mariusz-Rossa/CollatWheel.git
cd CollatzWheel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run tests before submitting a pull request:

```bash
python -m pytest tests/ -v
```

---

## Code style

- Python 3.12+
- Follow the existing style — docstrings, type hints, clear variable names
- One topic per commit, descriptive commit messages in English
- No external dependencies beyond `requirements.txt`

---

## Reporting issues

Please include:
- Python version (`python --version`)
- Operating system
- Minimal example that reproduces the problem
- Expected vs actual output

---

## Note on research direction

The core research hypotheses and mathematical framing are the author's own. Contributions that extend the empirical analysis (new ranges, new moduli, visualisations) are especially welcome. Contributions that challenge or refine existing findings are equally welcome — science works that way.

---

*This project is developed by an independent researcher. Response times may vary.*