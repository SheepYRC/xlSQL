

------

# 📦 xlsql 设计文档（MVP版）

------

# 一、项目目标

`xlsql` 是一个**面向 AI Agent 的本地数据查询 CLI 工具**，用于对 Excel / CSV / JSON 文件进行 SQL 查询。

设计原则：

- 简单（最少命令）
- AI友好（结构化输出 + 可预测行为）
- 本地执行（无需服务）
- 即下即用（无需复杂安装）

------

# 二、CLI Spec（命令设计）

工具名：

```bash
xlsql
```

------

## 1️⃣ query（核心查询）

```bash
xlsql query \
  --file sales.xlsx \
  --file users.json \
  --sql "SELECT * FROM sales" \
  --limit 100 \
  --output result.json
```

### 参数说明：

| 参数       | 说明                              |
| ---------- | --------------------------------- |
| `--file`   | 支持多个文件（xlsx / csv / json） |
| `--sql`    | SQL 查询语句                      |
| `--limit`  | 默认 100，防止返回过大            |
| `--output` | 可选，输出到文件                  |

------

## 2️⃣ schema（结构查看）

```bash
xlsql schema --file sales.xlsx --file users.json
```

用途：

- 获取表名
- 获取列名和类型
- 给 AI 写 SQL 提供依据

------

## 3️⃣ preview（数据预览）

```bash
xlsql preview --file sales.xlsx --rows 20
```

用途：

- 查看原始数据结构
- 判断是否需要预处理

------

## 4️⃣ prepare（数据预处理）

```bash
xlsql prepare \
  --file raw.xlsx \
  --skip-rows 2 \
  --skip-cols 1 \
  --header-row 3 \
  --output clean.xlsx
```

### 参数说明：

| 参数           | 说明                     |
| -------------- | ------------------------ |
| `--skip-rows`  | 跳过前N行                |
| `--skip-cols`  | 跳过前N列                |
| `--header-row` | 指定表头行               |
| `--output`     | 输出文件（默认自动生成） |

------

### 默认输出规则：

```text
raw.xlsx → raw_cleaned.xlsx
```

------

# 三、JSON 输出协议（统一结构）

所有命令统一返回：

```json
{
  "ok": true,
  "data": {...},
  "error": null
}
```

------

## ✅ 成功示例（query）

```json
{
  "ok": true,
  "data": {
    "columns": ["region", "total_sales"],
    "rows": [
      ["APAC", 10000],
      ["EMEA", 8000]
    ],
    "row_count": 2,
    "truncated": false
  },
  "error": null
}
```

------

## ❌ 错误示例

```json
{
  "ok": false,
  "data": null,
  "error": "Column 'amt' not found"
}
```

------

## ✅ schema 示例

```json
{
  "ok": true,
  "data": {
    "tables": [
      {
        "name": "sales",
        "columns": [
          {"name": "region", "type": "STRING"},
          {"name": "amount", "type": "DOUBLE"}
        ]
      }
    ]
  },
  "error": null
}
```

------

## ✅ prepare 示例

```json
{
  "ok": true,
  "data": {
    "output_file": "clean.xlsx",
    "columns": ["region", "amount"],
    "row_count": 1200
  },
  "error": null
}
```

------

# 四、Python MVP 架构

------

## 📁 项目结构

```text
xlsql/
 ├── cli.py
 ├── engine.py
 ├── loader.py
 ├── prepare.py
 ├── utils.py
 └── requirements.txt
```

------

## 依赖

```txt
duckdb
pandas
openpyxl
```

------

# 五、核心实现

------

## 1️⃣ cli.py

```python
import argparse
from engine import run_query, get_schema, preview_data
from prepare import run_prepare

def main():
    parser = argparse.ArgumentParser(prog="xlsql")
    subparsers = parser.add_subparsers(dest="command")

    # query
    q = subparsers.add_parser("query")
    q.add_argument("--file", action="append", required=True)
    q.add_argument("--sql", required=True)
    q.add_argument("--limit", type=int, default=100)
    q.add_argument("--output")

    # schema
    s = subparsers.add_parser("schema")
    s.add_argument("--file", action="append", required=True)

    # preview
    p = subparsers.add_parser("preview")
    p.add_argument("--file", required=True)
    p.add_argument("--rows", type=int, default=20)

    # prepare
    pr = subparsers.add_parser("prepare")
    pr.add_argument("--file", required=True)
    pr.add_argument("--skip-rows", type=int, default=0)
    pr.add_argument("--skip-cols", type=int, default=0)
    pr.add_argument("--header-row", type=int, default=1)
    pr.add_argument("--output")

    args = parser.parse_args()

    if args.command == "query":
        run_query(args)
    elif args.command == "schema":
        get_schema(args)
    elif args.command == "preview":
        preview_data(args)
    elif args.command == "prepare":
        run_prepare(args)

if __name__ == "__main__":
    main()
```

------

## 2️⃣ loader.py

```python
import pandas as pd
import os

def load_files(con, files):
    for file in files:
        name = os.path.splitext(os.path.basename(file))[0]

        if file.endswith(".xlsx"):
            df = pd.read_excel(file)
        elif file.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.endswith(".json"):
            df = pd.read_json(file)
        else:
            raise Exception(f"Unsupported file: {file}")

        con.register(name, df)
```

------

## 3️⃣ engine.py

```python
import duckdb
import json
from loader import load_files

def success(data):
    return {"ok": True, "data": data, "error": None}

def fail(msg):
    return {"ok": False, "data": None, "error": msg}


def run_query(args):
    con = duckdb.connect()
    try:
        load_files(con, args.file)

        sql = f"{args.sql} LIMIT {args.limit}"
        df = con.execute(sql).fetchdf()

        result = success({
            "columns": list(df.columns),
            "rows": df.values.tolist(),
            "row_count": len(df),
            "truncated": len(df) == args.limit
        })

    except Exception as e:
        result = fail(str(e))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f)
    else:
        print(json.dumps(result, indent=2))


def get_schema(args):
    con = duckdb.connect()
    try:
        load_files(con, args.file)

        tables = []
        for f in args.file:
            name = f.split("/")[-1].split(".")[0]
            df = con.execute(f"SELECT * FROM {name} LIMIT 0").df()

            tables.append({
                "name": name,
                "columns": [
                    {"name": c, "type": str(t)}
                    for c, t in zip(df.columns, df.dtypes)
                ]
            })

        print(json.dumps(success({"tables": tables}), indent=2))

    except Exception as e:
        print(json.dumps(fail(str(e)), indent=2))


def preview_data(args):
    con = duckdb.connect()
    try:
        load_files(con, [args.file])
        name = args.file.split("/")[-1].split(".")[0]

        df = con.execute(f"SELECT * FROM {name} LIMIT {args.rows}").df()

        print(df.to_string())

    except Exception as e:
        print(json.dumps(fail(str(e)), indent=2))
```

------

## 4️⃣ prepare.py（新增）

```python
import pandas as pd
import os
import json

def run_prepare(args):
    try:
        df = pd.read_excel(args.file)

        # skip rows
        if args.skip_rows > 0:
            df = df.iloc[args.skip_rows:]

        # skip cols
        if args.skip_cols > 0:
            df = df.iloc[:, args.skip_cols:]

        # header
        header_idx = args.header_row - 1
        df.columns = df.iloc[header_idx]
        df = df[(header_idx + 1):]

        # output
        if args.output:
            out = args.output
        else:
            base, ext = os.path.splitext(args.file)
            out = f"{base}_cleaned{ext}"

        df.to_excel(out, index=False)

        result = {
            "ok": True,
            "data": {
                "output_file": out,
                "columns": list(df.columns),
                "row_count": len(df)
            },
            "error": None
        }

    except Exception as e:
        result = {
            "ok": False,
            "data": None,
            "error": str(e)
        }

    print(json.dumps(result, indent=2))
```

------

# 六、AI 使用模式（配合 skill.md）

推荐流程：

```text
preview → (判断是否 messy) → prepare → schema → query
```

------

# 七、分发方式（当前阶段）

推荐：

```text
zip 包：
- 源码
- requirements.txt
- skill.md
- README.md
```

用户使用包管理工具：

```bash
pip install -r requirements.txt
python cli.py ...
```

------

# 八、MVP范围（刻意限制）

当前版本只包含：

- query
- schema
- preview
- prepare

------

不包含：

- ❌ 自动清洗
- ❌ 自然语言转SQL
- ❌ UI界面
- ❌ pip发布

------

# ✅ 最终总结

这个版本的 xlsql：

- 是一个 **AI优先的CLI工具**
- 通过 **结构化输出 + 明确命令** 提供能力
- 通过 **skill.md** 提供智能行为

本质上是：

> 👉 一个“让 AI 稳定操作数据”的最小系统

------

