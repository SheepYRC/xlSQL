import duckdb
from .loader import load_files
from .utils import success, fail, print_result

def run_query(args):
    """
    执行 SQL 查询。
    """
    con = duckdb.connect()
    try:
        load_files(con, args.file)

        # 使用子查询限制结果集，防止 LIMIT 冲突
        sql = f"SELECT * FROM ({args.sql}) LIMIT {args.limit}"
        
        # 使用 Polars 获取结果
        df = con.execute(sql).pl()

        result = success({
            "columns": list(df.columns),
            "rows": df.to_dicts(),
            "row_count": len(df),
            "truncated": len(df) == args.limit
        })

    except Exception as e:
        result = fail(e)

    if hasattr(args, 'output') and args.output:
        import json
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    else:
        print_result(result)


def get_schema(args):
    """
    获取表结构信息。
    """
    con = duckdb.connect()
    try:
        load_files(con, args.file)

        tables = []
        for f in args.file:
            import os
            name = os.path.splitext(os.path.basename(f))[0]
            
            # 使用 Polars 获取 schema，对表名加双引号防止特殊字符导致的语法错误
            df = con.execute(f'SELECT * FROM "{name}" LIMIT 0').pl()

            tables.append({
                "name": name,
                "columns": [
                    {"name": c, "type": str(t)}
                    for c, t in zip(df.columns, df.dtypes)
                ]
            })

        print_result(success({"tables": tables}))

    except Exception as e:
        print_result(fail(e))


def preview_data(args):
    """
    控制台预览数据。
    """
    con = duckdb.connect()
    try:
        load_files(con, [args.file])
        import os
        name = os.path.splitext(os.path.basename(args.file))[0]
        
        # 对表名加双引号
        df = con.execute(f'SELECT * FROM "{name}" LIMIT {args.rows}').pl()

        print(f"--- 数据预览: {args.file} ({len(df)} rows) ---")
        print(str(df)) 

    except Exception as e:
        print_result(fail(e))
