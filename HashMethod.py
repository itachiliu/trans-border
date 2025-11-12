import hashlib


def hash_file(filename, hash_algorithm='sha256'):
    """计算文件的哈希值"""
    # 创建一个hash对象
    hash_obj = getattr(hashlib, hash_algorithm)()

    # 以二进制读取模式打开文件
    with open(filename, 'rb') as file:
        # 读取文件内容，并更新hash对象
        for chunk in iter(lambda: file.read(4096), b""):
            hash_obj.update(chunk)

    # 返回十六进制编码的哈希值
    return hash_obj.hexdigest()

