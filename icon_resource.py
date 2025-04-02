import base64
import os
import sys

# 获取图标路径
base_path = os.path.dirname(os.path.abspath(__file__)) if not hasattr(sys, '_MEIPASS') else sys._MEIPASS
icon_path = os.path.join(base_path, 'icons', '2fa.ico')

# 将图标转换为base64字符串
with open(icon_path, 'rb') as icon_file:
    ICON_BASE64 = base64.b64encode(icon_file.read()).decode('utf-8')
