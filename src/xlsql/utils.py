import json

def success(data):
    """返回统一的成功响应格式"""
    return {"ok": True, "data": data, "error": None}

def fail(msg):
    """返回统一的错误响应格式"""
    return {"ok": False, "data": None, "error": str(msg)}

def print_result(result, indent=2):
    """打印 JSON 结果"""
    print(json.dumps(result, indent=indent, ensure_ascii=False))
