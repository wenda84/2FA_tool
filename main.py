import pyotp
import time
import base64
import hashlib
import sys
import os
import json
from io import BytesIO
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QByteArray
from gui import MainWindow

CONFIG_FILE = "config.json"

# 获取脚本所在目录的路径
script_dir = os.path.dirname(os.path.abspath(__file__))

# 构建 JSON 文件的完整路径
CONFIG_FILE_PATH = os.path.join(script_dir, CONFIG_FILE)

def encrypt_b64(key, plaintext):
    encrypted_data = b''
    for i in range(len(plaintext)):
        key_index = i % len(key)
        encrypted_data += bytes([(ord(plaintext[i]) ^ ord(key[key_index])) & 0xFF])

    return base64.urlsafe_b64encode(encrypted_data).decode()

def decrypt_b64(key, ciphertext):
    ciphertext = base64.urlsafe_b64decode(ciphertext)
    decrypted_text = ''
    for i in range(len(ciphertext)):
        key_index = i % len(key)
        decrypted_text += chr((ciphertext[i] ^ ord(key[key_index])) & 0xFF)
    return decrypted_text

def save_config(config):
    with open(CONFIG_FILE_PATH, 'w') as file:
        json.dump(config, file, indent=2)

def load_config():
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as file:
            return json.load(file)
    else:
        return None

def get_icon():
    from icon_resource import ICON_BASE64
    icon_data = base64.b64decode(ICON_BASE64)
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray(icon_data))
    return QIcon(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(get_icon())  # 使用base64图标
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 移除重复的图标设置，因为已经在应用程序级别设置过了
