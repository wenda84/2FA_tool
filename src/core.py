import pyotp
import base64
import hashlib
import os
import json
import sys

# 修改配置文件路径逻辑
CONFIG_FILE = "2fa_tool_config.json"

def get_application_path():
    """获取应用程序路径，兼容exe和py文件"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        return os.path.dirname(sys.executable)
    else:
        # 如果是python脚本
        return os.path.dirname(os.path.abspath(__file__))

APP_DATA_DIR = get_application_path()
CONFIG_FILE_PATH = os.path.join(APP_DATA_DIR, CONFIG_FILE)

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

def get_resource_path(relative_path):
    """获取资源文件的完整路径，支持开发环境和打包环境"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        base_path = sys._MEIPASS
    else:
        # 如果是python脚本
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class TOTPManager:
    CONFIG_FILE_PATH = CONFIG_FILE_PATH  # 添加类属性以便外部访问
    
    def __init__(self):
        # 确保配置目录存在
        if not os.path.exists(APP_DATA_DIR):
            os.makedirs(APP_DATA_DIR)
        self.config = self.load_config()
        self.personal_key = None
        # 根据配置文件初始化skip_password
        self.skip_password = self.config.get("skip_password", False)
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r') as file:
                config = json.load(file)
                # 处理旧版本配置文件升级
                if "encrypted_secret_key" in config:
                    # 转换旧格式到新格式
                    new_config = {
                        "platforms": {
                            "default": config["encrypted_secret_key"]
                        },
                        "md5_hash": config["md5_hash"]
                    }
                    # 保存新格式
                    with open(CONFIG_FILE_PATH, 'w') as f:
                        json.dump(new_config, f, indent=2)
                    return new_config
                # 确保platforms字段存在
                if "platforms" not in config:
                    config["platforms"] = {}
                return config
        return {"platforms": {}, "md5_hash": ""}
    
    def save_config(self):
        with open(CONFIG_FILE_PATH, 'w') as file:
            json.dump(self.config, file, indent=2)
            
    def set_skip_password(self):
        self.skip_password = True
        self.config["skip_password"] = True
        self.config["md5_hash"] = ""  # 清除密码hash
        self.personal_key = ""  # 使用空密码
        self.save_config()
        return True

    def set_personal_key(self, key):
        if self.config.get("skip_password", False):
            self.personal_key = ""
            return True
        if not self.config.get("md5_hash"):
            self.config["md5_hash"] = hashlib.md5(key.encode()).hexdigest()
            self.config["skip_password"] = False  # 设置密码时明确标记不跳过密码
            self.save_config()
        elif hashlib.md5(key.encode()).hexdigest() != self.config["md5_hash"]:
            return False
        self.personal_key = key
        return True
        
    def add_platform(self, name, secret_key):
        if not self.personal_key and not self.config.get("skip_password", False):
            raise Exception("需要先设置个人密码")
            
        if self.skip_password:
            # 无密码模式下直接保存原始密钥
            self.config["platforms"][name] = secret_key
        else:
            # 有密码模式下加密保存
            encrypted_key = encrypt_b64(self.personal_key, secret_key)
            self.config["platforms"][name] = encrypted_key
        self.save_config()
        
    def remove_platform(self, name):
        if name in self.config["platforms"]:
            del self.config["platforms"][name]
            self.save_config()
            
    def get_totp(self, platform_name):
        if not self.personal_key and not self.config.get("skip_password", False):
            raise Exception("需要先设置个人密码")
        if platform_name not in self.config["platforms"]:
            raise Exception("平台不存在")
        
        secret_key = self.config["platforms"][platform_name]
        if not self.skip_password:
            # 有密码模式下需要解密
            secret_key = decrypt_b64(self.personal_key, secret_key)
        
        totp = pyotp.TOTP(secret_key)
        return totp.now()

    def get_platforms(self):
        return list(self.config["platforms"].keys())