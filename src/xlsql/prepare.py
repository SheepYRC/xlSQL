import polars as pl
import os
from .utils import success, fail, print_result

def run_prepare(args):
    """
    预处理 Excel 文件（跳行、裁减、重设表头）。
    """
    try:
        # 加载 Excel 文件，暂不自动识别表头
        df = pl.read_excel(args.file, has_header=False)

        # 跳过前 N 行 (含可能的垃圾行)
        if args.skip_rows > 0:
            df = df.slice(args.skip_rows)

        # 跳过前 N 列
        if args.skip_cols > 0:
            df = df.select(df.columns[args.skip_cols:])

        header_idx = args.header_row - 1
        if header_idx < 0:
            header_idx = 0

        # 获取指定行作为新列名
        try:
            header_row_data = df.row(header_idx)
            new_columns = [str(x) if (x is not None and str(x).strip() != "") else f"column_{i+1}" 
                           for i, x in enumerate(header_row_data)]
        except IndexError:
            raise Exception(f"无法找到表头行: 第 {args.header_row} 行不存在 (可能 skip-rows 过大)")
        
        # 裁剪数据 (表头之后的行)
        df = df.slice(header_idx + 1)
        
        # 重命名列
        df = df.rename({old: new for old, new in zip(df.columns, new_columns)})

        # 确定输出文件名
        if args.output:
            out = args.output
        else:
            base, _ = os.path.splitext(args.file)
            out = f"{base}_cleaned.xlsx" # 统一输出为新版 excel

        # 保存为 Excel 文件
        df.write_excel(out)

        result = success({
            "output_file": out,
            "columns": list(df.columns),
            "row_count": len(df)
        })

    except Exception as e:
        result = fail(e)

    print_result(result)
