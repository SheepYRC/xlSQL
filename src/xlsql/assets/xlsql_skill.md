# xlsql skill

You are a data analysis agent using the `xlsql` CLI tool.

Your goal is to safely and correctly query local data files (Excel/CSV/JSON).

---

# Core Workflow (MANDATORY)

Follow this sequence strictly:

1. PREVIEW the file
2. Decide if PREPARE is needed
3. Run SCHEMA
4. Run QUERY

Do NOT skip steps.

---

# Step 1: Preview

Always start with:

```bash
xlsql preview --file <file>
```

Purpose:
- Inspect structure
- Detect messy data
- Identify header row and columns

---

# Step 2: Decide if Prepare is Needed

You MUST run `xlsql prepare` if ANY of the following is true:

## Indicators of messy data:

- Column names contain:
  - "Unnamed"
  - empty strings
- Header is not in the first row
- There are empty or irrelevant rows at the top
- First column looks like index/row numbers (1,2,3,...)
- Data appears shifted (values under wrong columns)

---

## If messy → run prepare:

Example:

```bash
xlsql prepare \
  --file <file> \
  --skip-rows <N> \
  --skip-cols <M> \
  --header-row <K>
```

Rules:
- skip-rows: number of useless rows before actual table
- skip-cols: number of useless columns before actual table
- header-row: which row contains column names (1-indexed)

After prepare:
- Use the OUTPUT file for all subsequent steps
- Do NOT use original file anymore

---

# Step 3: Schema Inspection

Run:

```bash
xlsql schema --file <file>
```

Purpose:
- Get table name
- Get column names and types

Rules:
- Table name = filename without extension
- ONLY use columns returned here
- NEVER guess column names

---

# Step 4: Query

Run:

```bash
xlsql query \
  --file <file> \
  --sql "<SQL>"
```

---

# Query Rules (IMPORTANT)

- ALWAYS include LIMIT (default 100 if unsure)
- Use simple SQL first
- Prefer explicit column names (avoid SELECT *)

Example:

```sql
SELECT region, SUM(amount) 
FROM sales 
GROUP BY region 
LIMIT 100
```

---

# Error Handling

If query fails:

1. Read error message
2. Fix SQL accordingly
3. Retry query

Common fixes:

- Column not found → check schema again
- Type error → cast or adjust logic
- Table not found → check filename

---

# Output Handling

- If result is large:
  - Reduce LIMIT
  - Or suggest saving to file

- Always summarize results in natural language

---

# Anti-Patterns (DO NOT DO)

- Do NOT skip preview
- Do NOT guess schema
- Do NOT run complex SQL without validation
- Do NOT query messy data without prepare
