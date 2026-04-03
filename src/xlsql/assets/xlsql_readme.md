# Data Project with xlSQL

This project uses `xlSQL` for data querying and analysis.

## Tools Required

- [uv](https://docs.astral.sh/uv/) - Python package management
- [xlsql](https://github.com/TODO/xlsql) - Local SQL query tool for Excel/CSV/JSON

## How to use

Run SQL queries directly against your local data files.

**Windows Tip**: Use square brackets `[ ]` for table names to avoid complex quote escaping in terminals.

```bash
xlsql query --file ./data/sales.xlsx --sql "SELECT * FROM [sales] WHERE amount > 1000 LIMIT 10"
```

## AI Agent Integration

This project includes a `xlsql_skill.md` file designed to help AI agents (like Cursor, Windsurf, or Antigravity) understand how to best use the `xlsql` CLI. Make sure your agent reads this file before starting data tasks.
