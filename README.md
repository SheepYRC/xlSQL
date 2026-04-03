# xlSQL

面向 AI Agent 的本地数据查询 CLI 工具，用于对 Excel / CSV / JSON 文件进行 SQL 查询。

## 特性

- **简单**: 极简的命令设计。
- **AI 友好**: 统一的 JSON 结构化输出。
- **本地执行**: 基于 DuckDB 和 Pandas，无需数据库服务。
- **功能完备**: 支持查询、结构查看、预览及数据预处理。

## 安装与分发 (Recommended)

本项目支持通过 `uv tool` 进行全局安装，实现随处调用。

```bash
# 方式 A: 直接从源码安装 (当前目录)
uv tool install .

# 方式 B: 从远程 Git 仓库安装 (替换为您的仓库地址)
# uv tool install git+https://github.com/yourname/xlsql.git
uv tool install git+https://github.com/SheepYRC/xlSQL.git
```

安装完成后，您可以直接在终端输入 `xlsql` 进行操作：
```bash
xlsql --help
```

## 常规开发运行
如果你只是想在当前环境下进行开发：

```bash
# 安装依赖并运行
uv run xlsql query --file sales.csv --sql "SELECT * FROM sales"
```

## 核心命令

### 1. `query` (数据查询)
```bash
xlsql query --file data.xlsx --file info.json --sql "SELECT * FROM data JOIN info ON data.id = info.id"
```

### 2. `schema` (查看结构)
```bash
xlsql schema --file data.xlsx
```

### 3. `preview` (预览数据)
```bash
xlsql preview --file data.xlsx --rows 10
```

### 4. `prepare` (数据预处理)
用于处理表头杂乱的 Excel 文件。
```bash
xlsql prepare --file messy.xlsx --skip-rows 2 --header-row 1 --output clean.xlsx
```

### 5. `init` (初始化项目资源)
在当前目录下生成 xlsql 相关的辅助文档，以便 AI Agent 更好地协助你。
```bash
# 初始化所有资源 (xlsql_skill.md 和 xlsql_readme.md)
xlsql init --all

# 仅初始化 AI Agent 技能说明
xlsql init --skill
```

## AI Agent 集成指南

强烈建议在数据分析项目中使用 `xlsql init --skill`。这会生成一份 `xlsql_skill.md`。你可以将其内容提供给 Cursor / Windsurf / Antigravity 等 AI 编程助手，它们将获得如何利用 `xlsql` 进行安全、高效数据查询的完整操作指南，包括预览数据、处理杂乱表头及基于 Polars/DuckDB 的 SQL 查询最佳实践。

## 技术栈

- **Python**: 3.12+
- **DuckDB**: 极速 SQL 引擎
- **Polars**: 高性能 DataFrame 库 (替代 Pandas)
- **uv**: 现代依赖管理
