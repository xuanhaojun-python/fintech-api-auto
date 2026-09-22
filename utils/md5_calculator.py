import hashlib


def calculate_md5(file_path):
    """计算文件的MD5值"""
    md5_hash = hashlib.md5()

    try:
        with open(file_path, "rb") as f:
            # 分块读取文件，避免大文件占用过多内存
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)

        return md5_hash.hexdigest()
    except FileNotFoundError:
        return "文件未找到"
    except Exception as e:
        return f"发生错误: {str(e)}"


if __name__ == '__main__':
    response = calculate_md5("/Users/photonpay/Downloads/Codex橙皮书.pdf")
    print(response)
