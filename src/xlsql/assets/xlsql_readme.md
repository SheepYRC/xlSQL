# Data Project with xlSQL

This project uses `xlSQL` for data querying and analysis.

## Tools Required

- [uv](https://docs.astral.sh/uv/) - Python package management
- [xlsql](https://github.com/TODO/xlsql) - Local SQL query tool for Excel/CSV/JSON

## How to use

Run SQL queries directly against your local data files:

```bash
xlsql query --file ./data/your_file.csv --sql "SELECT * FROM your_file LIMIT 10"
```

## AI Agent Integration

This project includes a `xlsql_skill.md` file designed to help AI agents (like Cursor, Windsurf, or Antigravity) understand how to best use the `xlsql` CLI. Make sure your agent reads this file before starting data tasks.
