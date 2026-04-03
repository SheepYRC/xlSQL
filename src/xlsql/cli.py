import argparse
import sys
from .engine import run_query, get_schema, preview_data
from .prepare import run_prepare

def main():
    parser = argparse.ArgumentParser(prog="xlsql", description="面向 AI Agent 的本地数据查询 CLI 工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. query 子命令
    q_parser = subparsers.add_parser("query", help="执行 SQL 查询")
    q_parser.add_argument("--file", action="append", required=True, help="要查询的文件路径（可指定多个）")
    q_parser.add_argument("--sql", required=True, help="SQL 查询语句")
    q_parser.add_argument("--limit", type=int, default=100, help="限制返回行数 (默认值: 100)")
    q_parser.add_argument("--output", help="输出查询结果到 JSON 文件")

    # 2. schema 子命令
    s_parser = subparsers.add_parser("schema", help="查看数据表结构")
    s_parser.add_argument("--file", action="append", required=True, help="要查询的文件路径（可指定多个）")

    # 3. preview 子命令
    p_parser = subparsers.add_parser("preview", help="预览原始数据")
    p_parser.add_argument("--file", required=True, help="要预览的文件路径")
    p_parser.add_argument("--rows", type=int, default=20, help="预览行数 (默认值: 20)")

    # 4. prepare 子命令
    pr_parser = subparsers.add_parser("prepare", help="预处理杂乱的 Excel 数据")
    pr_parser.add_argument("--file", required=True, help="要处理的 Excel 文件路径")
    pr_parser.add_argument("--skip-rows", type=int, default=0, help="跳过前 N 行")
    pr_parser.add_argument("--skip-cols", type=int, default=0, help="跳过前 N 列")
    pr_parser.add_argument("--header-row", type=int, default=1, help="指定表头行 (1-indexed)")
    pr_parser.add_argument("--output", help="输出文件路径（默认自动生成）")
    
    # 5. init 子命令
    init_parser = subparsers.add_parser("init", help="在当前目录初始化 xlsql 相关的资源")
    init_parser.add_argument("--skill", action="store_true", help="初始化 xlsql_skill.md (面向 AI Agent)")
    init_parser.add_argument("--readme", action="store_true", help="初始化 xlsql_readme.md (参考文档)")
    init_parser.add_argument("--all", action="store_true", help="初始化所有资源")

    args = parser.parse_args()

    # 命令调度
    if args.command == "query":
        run_query(args)
    elif args.command == "schema":
        get_schema(args)
    elif args.command == "preview":
        preview_data(args)
    elif args.command == "prepare":
        run_prepare(args)
    elif args.command == "init":
        run_init(args)

def run_init(args):
    """
    初始化当前目录的项目资源。
    """
    import os
    try:
        from importlib import resources
        import shutil

        # 定义资源映射 {(资源名, 目标文件名)}
        resources_to_copy = []
        if args.skill or args.all:
            resources_to_copy.append(("xlsql_skill.md", "xlsql_skill.md"))
        if args.readme or args.all:
            resources_to_copy.append(("xlsql_readme.md", "xlsql_readme.md"))
            
        if not resources_to_copy and not args.all:
            print("请指定要初始化的项: --skill, --readme 或 --all")
            return

        try:
            assets = resources.files("xlsql.assets")
        except (ModuleNotFoundError, ImportError, TypeError):
            # 开发环境回退逻辑: 如果无法通过包名找到，则从脚本所在位置查找
            base_dir = os.path.dirname(os.path.abspath(__file__))
            assets = os.path.join(base_dir, "assets")
            # 转换为 pathlib 对象模拟 resources.files 的 API
            from pathlib import Path
            assets = Path(assets)

        for asset_name, target_name in resources_to_copy:
            source_path = assets.joinpath(asset_name)
            if not source_path.exists():
                print(f"警告: 资源 {asset_name} 未在包内找到 (Path: {source_path})")
                continue

            if os.path.exists(target_name):
                print(f"跳过: {target_name} 已存在于当前目录")
            else:
                with source_path.open('rb') as f_in:
                    with open(target_name, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"已创建: {target_name}")

        print("\n初始化完成！你可以尝试将 xlsql_skill.md 提供给你的 AI Agent 协助数据分析。")

    except Exception as e:
        print(f"初始化失败: {e}")

if __name__ == "__main__":
    main()
