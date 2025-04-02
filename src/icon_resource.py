import base64
import os
import sys

def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        # 如果是打包后的环境
        return os.path.join(sys._MEIPASS, 'icons')
    else:
        # 开发环境
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resource')

# 获取图标路径
icon_path = os.path.join(get_base_path(), '2fa.ico')

try:
    # 将图标转换为base64字符串
    with open(icon_path, 'rb') as icon_file:
        ICON_BASE64 = base64.b64encode(icon_file.read()).decode('utf-8')
except FileNotFoundError:
    print(f"错误: 无法找到图标文件: {icon_path}")
    ICON_BASE64 = ""  # 设置默认空值
