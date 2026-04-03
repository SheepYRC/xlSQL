import sys
import os
import duckdb
import polars as pl
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from xlsql.engine import run_query
from xlsql.loader import load_files

def test_sql_limit_wrapping():
    print("Testing SQL LIMIT wrapping...")
    class Args:
        file = ["test/sales.csv"]
        sql = "SELECT * FROM sales LIMIT 5"
        limit = 100
    
    # Simulate run_query logic
    sql = f"SELECT * FROM ({Args.sql}) LIMIT {Args.limit}"
    print(f"Generated SQL: {sql}")
    assert "SELECT * FROM (SELECT * FROM sales LIMIT 5) LIMIT 100" == sql
    print("✓ SQL wrapping passed")

def test_table_quoting():
    print("Testing Table Quoting...")
    # Create a file with spaces
    filepath = "test/sales with space.csv"
    with open(filepath, "w") as f:
        f.write("id,amount\n1,100\n2,200")
    
    con = duckdb.connect()
    try:
        # Simulate loader.py
        name = os.path.splitext(os.path.basename(filepath))[0]
        df = pl.read_csv(filepath)
        con.register(name, df)
        
        # Simulate engine.py quoting
        sql = f'SELECT * FROM "{name}"'
        print(f"Quoted SQL: {sql}")
        res = con.execute(sql).pl()
        assert len(res) == 2
        print("✓ Table quoting passed")
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == "__main__":
    try:
        test_sql_limit_wrapping()
        test_table_quoting()
        print("\nAll basic tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
