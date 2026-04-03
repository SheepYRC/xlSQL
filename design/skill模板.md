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

xlsql preview --file <file>

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

xlsql prepare \
  --file <file> \
  --skip-rows <N> \
  --skip-cols <M> \
  --header-row <K>

Rules:
- skip-rows: number of useless rows before actual table
- skip-cols: number of useless columns before actual table
- header-row: which row contains column names

After prepare:
- Use the OUTPUT file for all subsequent steps
- Do NOT use original file anymore

---

# Step 3: Schema Inspection

Run:

xlsql schema --file <file>

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

xlsql query \
  --file <file> \
  --sql "<SQL>"

---

# Query Rules (IMPORTANT)

- ALWAYS include LIMIT (default 100 if unsure)
- Use simple SQL first
- Prefer explicit column names (avoid SELECT *)

Example:

SELECT region, SUM(amount) 
FROM sales 
GROUP BY region 
LIMIT 100

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

---

# SQL Auto-Fix Strategy (MANDATORY)

If a query fails, you MUST follow this repair process.

---

## Step 1: Read Error Carefully

Identify the error type:

- Column not found
- Table not found
- Syntax error
- Type mismatch
- Other

---

## Step 2: Apply Fix Rules

### Case 1: Column Not Found

Error example:
"Column 'amt' not found"

Action:
- Re-run: xlsql schema
- Find closest matching column name
- Replace with correct column

---

### Case 2: Table Not Found

Action:
- Check filename
- Table name = filename without extension
- Fix SQL table name

---

### Case 3: Syntax Error

Common issues:
- Missing commas
- Wrong quotes
- Invalid SQL structure

Action:
- Simplify query
- Start with basic SELECT

---

### Case 4: Type Mismatch

Example:
SUM() on string column

Action:
- Check schema types
- Cast if needed:
  CAST(column AS DOUBLE)

---

### Case 5: Unknown Error

Action:
- Reduce query complexity
- Try:

SELECT * FROM table LIMIT 10

Then rebuild query step by step

---

## Step 3: Retry Query

- Apply fix
- Run query again

---

## Retry Rules

- Maximum 3 attempts
- Each attempt must modify SQL
- If still failing:
  - Fall back to simple query
  - Explain limitation

---

## Fallback Strategy (IMPORTANT)

If complex query fails repeatedly:

1. Run simple query:

SELECT * FROM table LIMIT 10

2. Analyze data
3. Try simpler aggregation

---

## Anti-Patterns

- Do NOT repeat same SQL
- Do NOT guess blindly
- Do NOT increase complexity after failure

---

# Prepare Parameter Inference (IMPORTANT)

When data looks messy, you should TRY to infer correct prepare parameters before calling `xlsql prepare`.

---

## Step 1: Analyze Preview Output

From `xlsql preview`, identify:

- Where actual header row is
- Whether there are useless rows at top
- Whether there are useless columns at left

---

## Step 2: Infer Parameters

### Infer header-row

Look for the row where:
- Most cells are non-empty
- Values look like column names (strings, not numbers)
- No repeated patterns like 1,2,3,...

Example:

Row 1: empty  
Row 2: report title  
Row 3: region | amount | date  ← use this

→ header-row = 3

---

### Infer skip-rows

skip-rows = number of rows BEFORE header-row

Example:
- header-row = 3  
  → skip-rows = 2

---

### Infer skip-cols

Look at leftmost columns:

If first column:
- is empty
- or looks like row index (1,2,3,...)

→ skip-cols = 1

If multiple empty columns → increase accordingly

---

## Step 3: Call Prepare

Example:

xlsql prepare \
  --file raw.xlsx \
  --skip-rows 2 \
  --skip-cols 1 \
  --header-row 3

---

## Step 4: Validate Result

After prepare:

1. Run preview again
2. Check:
   - Column names are clean
   - No "Unnamed" columns
   - Data aligned correctly

If still messy:
- Adjust parameters
- Retry prepare

---

## Heuristics (Very Important)

- If unsure → prefer SMALL adjustments
  - start with skip-rows = 1 or 2
- Never skip too many rows at once
- Never assume header is row 1 if preview contradicts

---

## Fallback Strategy

If you cannot confidently infer parameters:

1. Try minimal clean:

xlsql prepare --skip-rows 1

2. Re-preview and refine

---

## Anti-Patterns

- Do NOT guess randomly
- Do NOT skip prepare when data is messy
- Do NOT use large skip values without validation

---

## Quick Pattern Recognition

Common patterns:

1. Title + table:
   Row 1: "Sales Report 2024"
   Row 2: empty
   Row 3: actual header
   → skip-rows = 2

2. Index column:
   First column = 1,2,3,...
   → skip-cols = 1

3. Empty padding:
   Top rows empty
   → skip-rows > 0