import polars as pl
import os

def load_files(con, files):
    """
    将文件加载到 DuckDB 连接中。
    
    :param con: DuckDB 连接对象
    :param files: 文件路径列表
    """
    for file in files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"文件不存在: {file}")
            
        name = os.path.splitext(os.path.basename(file))[0]

        if file.endswith(".xlsx") or file.endswith(".xls"):
            # 使用 fastexcel 引擎读取 Excel
            df = pl.read_excel(file)
        elif file.endswith(".csv"):
            df = pl.read_csv(file)
        elif file.endswith(".json"):
            # 尝试各种 JSON 格式
            try:
                df = pl.read_json(file)
            except:
                df = pl.read_ndjson(file)
        else:
            raise Exception(f"不支持的文件类型: {file}")

        # 注册 polars dataframe 到 DuckDB，表名默认为文件名（不含扩展名）
        con.register(name, df)
