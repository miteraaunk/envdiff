# envdiff

A CLI tool that compares `.env` files across environments and highlights missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git
cd envdiff && pip install .
```

---

## Usage

Compare two `.env` files:

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DEBUG
  - DEV_API_KEY

Mismatched keys:
  - DATABASE_URL  (values differ)

✔ All other keys match.
```

You can also compare multiple files at once:

```bash
envdiff .env.development .env.staging .env.production
```

Use `--keys-only` to suppress value comparison and check only for missing keys:

```bash
envdiff .env.development .env.production --keys-only
```

---

## Options

| Flag           | Description                              |
|----------------|------------------------------------------|
| `--keys-only`  | Only check for missing keys              |
| `--quiet`      | Suppress output, exit code signals diff  |
| `--json`       | Output results as JSON                   |

---

## License

[MIT](LICENSE)