from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QLineEdit, QLabel, QMessageBox, 
                             QInputDialog, QMenu, QApplication, QMenuBar, QDialog,
                             QCheckBox)
from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QColor, QPalette, QIcon
from core import TOTPManager, get_resource_path
import time
import sys
import os

class PasswordDialog(QDialog):
    def __init__(self, parent=None, title="输入密码", prompt="请输入密码:"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2f3542;
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
                margin: 5px 0;
            }
            QPushButton {
                background-color: #546de5;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #574bd6;
            }
        """)
        layout = QVBoxLayout(self)
        
        # 提示标签
        layout.addWidget(QLabel(prompt))
        
        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # 显示密码复选框
        self.show_password = QCheckBox("显示密码")
        self.show_password.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def toggle_password_visibility(self, checked):
        self.password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
    
    def get_password(self):
        return self.password_input.text()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2FA Tool")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2f3542;
            }
            QPushButton {
                background-color: #546de5;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #574bd6;
            }
            QPushButton:pressed {
                background-color: #45aaf2;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #546de5;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 2px;
            }
            QListWidget::item:selected {
                background-color: #546de5;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f1f2f6;
            }
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
                padding: 2px;
            }
            QMenu::item {
                padding: 4px 12px;
                min-width: 0px;  /* 移除最小宽度限制 */
            }
            QMenu::item:selected {
                background-color: #546de5;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #dcdde1;
                margin: 2px 0px;    /* 减小分隔符上下间距 */
            }
            QMenuBar {
                background-color: white;
            }
            QMenuBar::item {
                padding: 4px 8px;    /* 减小菜单栏项目内边距 */
            }
            QMenuBar::item:selected {
                background-color: #f1f2f6;
                border-radius: 2px;
            }
            QCheckBox {
                color: #2f3542;
            }
        """)
        self.totp_manager = TOTPManager()
        self.setup_menu()  # 添加菜单设置
        self.setup_ui()
        
    def setup_menu(self):
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        clear_action = file_menu.addAction("清除所有配置")
        clear_action.triggered.connect(self.clear_config)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("退出")
        exit_action.triggered.connect(self.close)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(self.show_about)

    def clear_config(self):
        reply = QMessageBox.warning(
            self,
            "确认清除",
            "确定要清除所有配置吗？\n这将删除所有平台数据和加密设置，此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除配置文件
                if os.path.exists(self.totp_manager.CONFIG_FILE_PATH):
                    os.remove(self.totp_manager.CONFIG_FILE_PATH)
                # 重新初始化
                QMessageBox.information(self, "提示", "配置已清除，程序将重新启动")
                QApplication.instance().quit()
                # 重启程序
                python = sys.executable
                os.execl(python, python, *sys.argv)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"清除配置失败: {str(e)}")

    def show_about(self):
        about_text = """
        <h3>2FA Tool</h3>
        <p>版本: 1.0.0</p>
        <p>一个简单的两步验证工具，支持：</p>
        <ul>
            <li>多平台管理</li>
            <li>加密保护</li>
            <li>验证码自动更新</li>
        </ul>
        <p>基于 Python 和 PySide6 开发</p>
        """
        QMessageBox.about(self, "关于", about_text)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)  # 增加边距
        layout.setSpacing(20)  # 增加控件间距
        
        # 左侧平台列表面板
        left_widget = QWidget()
        left_widget.setObjectName("leftPanel")
        left_widget.setStyleSheet("""
            #leftPanel {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        left_layout = QVBoxLayout(left_widget)
        self.platform_list = QListWidget()
        self.platform_list.currentItemChanged.connect(self.on_platform_selected)
        self.platform_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.platform_list.customContextMenuRequested.connect(self.show_context_menu)
        # 设置列表选择行为
        self.platform_list.setSelectionMode(QListWidget.SingleSelection)
        self.platform_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 5px;
                outline: none;  /* 移除焦点框 */
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 2px;
            }
            QListWidget::item:selected {
                background-color: #546de5;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #f1f2f6;
            }
        """)
        left_layout.addWidget(QLabel("已保存的平台:"))
        left_layout.addWidget(self.platform_list)
        
        # 添加平台控件
        add_platform_layout = QVBoxLayout()  # 改用垂直布局
        
        # 创建一个Label用于显示添加平台的表单
        form_label = QLabel()
        form_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 15px;
                background-color: #f1f2f6;
                border-radius: 6px;
                color: #2f3542;
            }
        """)
        
        # 将输入框封装在表格中
        self.platform_name_input = QLineEdit()
        self.platform_key_input = QLineEdit()
        self.platform_name_input.setStyleSheet("margin: 2px 0;")
        self.platform_key_input.setStyleSheet("margin: 2px 0;")
        
        form_label.setText(f"""
            <table style='border-spacing: 5px; border-collapse: separate;'>
                <tr>
                    <td style='text-align: left; width: 80px;'>平台名称:</td>
                    <td><input type='text' id='name_input'/></td>
                </tr>
                <tr>
                    <td style='text-align: left; width: 80px;'>密钥:</td>
                    <td><input type='text' id='key_input'/></td>
                </tr>
            </table>
        """)
        
        # 创建一个widget来容纳输入框
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(15, 15, 15, 15)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("平台名称:"), 0)
        name_layout.addWidget(self.platform_name_input, 1)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("密钥:"), 0)
        key_layout.addWidget(self.platform_key_input, 1)
        
        input_layout.addLayout(name_layout)
        input_layout.addLayout(key_layout)
        
        # 设置输入区域的样式
        input_widget.setStyleSheet("""
            QWidget {
                background-color: #f1f2f6;
                border-radius: 6px;
            }
            QLabel {
                min-width: 80px;
            }
        """)
        
        # 添加按钮
        add_btn = QPushButton("添加平台")
        add_btn.clicked.connect(self.add_platform)
        
        # 将所有控件添加到布局
        add_platform_layout.addWidget(input_widget)
        add_platform_layout.addWidget(add_btn)
        left_layout.addLayout(add_platform_layout)
        
        # 右侧验证码显示面板
        right_widget = QWidget()
        right_widget.setObjectName("rightPanel")
        right_widget.setStyleSheet("""
            #rightPanel {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        
        # 验证码显示区域
        self.code_label = QLabel("请选择平台")
        self.code_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                padding: 20px;
                background-color: #f1f2f6;
                border-radius: 6px;
                color: #2f3542;
            }
        """)
        # 设置固定宽度确保对齐
        self.code_label.setMinimumWidth(300)
        
        # 添加复制按钮
        copy_btn = QPushButton("复制验证码")
        copy_btn.clicked.connect(self.copy_code)
        
        right_layout.addWidget(self.code_label)
        right_layout.addWidget(copy_btn)
        right_layout.addStretch()  # 添加弹性空间
        
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        
        # 设置个人密码
        if not self.totp_manager.config["md5_hash"]:
            self.prompt_personal_key()
        else:
            self.verify_personal_key()
            
        # 更新平台列表
        self.update_platform_list()
        
        # 设置定时器更新验证码
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_current_code)
        self.timer.start(1000)
        
        # 设置固定大小和最小大小
        self.setMinimumSize(800, 600)
        
        # 设置窗口布局比例
        layout.setStretch(0, 3)  # 左侧面板占比
        layout.setStretch(1, 2)  # 右侧面板占比
        
    def prompt_personal_key(self):
        msg = "是否设置个人密码？\n设置密码可以加密保护您的平台密钥，不设置则明文保存。"
        reply = QMessageBox.question(self, "密码设置", msg,
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            while True:
                dialog = PasswordDialog(self, "设置个人密码", "请输入个人密码:")
                if dialog.exec() == QDialog.Accepted:
                    key = dialog.get_password()
                    if key:
                        self.totp_manager.set_personal_key(key)
                        break
                    QMessageBox.warning(self, "错误", "密码不能为空")
                else:
                    # 用户取消，默认选择跳过密码
                    self.totp_manager.set_skip_password()
                    break
        else:
            self.totp_manager.set_skip_password()

    def verify_personal_key(self):
        if self.totp_manager.config.get("skip_password", False):
            self.totp_manager.set_skip_password()
            return
            
        while True:
            dialog = PasswordDialog(self, "验证", "请输入个人密码:")
            if dialog.exec() != QDialog.Accepted:
                sys.exit(0)
            key = dialog.get_password()
            if self.totp_manager.set_personal_key(key):
                break
            QMessageBox.warning(self, "错误", "密码错误，请重试")
            
    def update_platform_list(self):
        self.platform_list.clear()
        self.platform_list.addItems(self.totp_manager.get_platforms())
        
    def add_platform(self):
        name = self.platform_name_input.text().strip()
        key = self.platform_key_input.text().strip()
        if name and key:
            try:
                self.totp_manager.add_platform(name, key)
                self.update_platform_list()
                self.platform_name_input.clear()
                self.platform_key_input.clear()
            except Exception as e:
                QMessageBox.warning(self, "错误", str(e))
                
    def on_platform_selected(self, current, previous):
        if current:
            self.update_current_code()
            
    def update_current_code(self):
        current_platform = self.platform_list.currentItem()
        if current_platform:
            try:
                code = self.totp_manager.get_totp(current_platform.text())
                remaining = 30 - (int(time.time()) % 30)
                platform_name = current_platform.text()
                # 使用HTML表格格式化显示，所有单元格左对齐
                self.code_label.setText(f"""
                    <table style='border-spacing: 10px; border-collapse: separate;'>
                        <tr>
                            <td style='text-align: left; width: 100px;'>平台:</td>
                            <td style='text-align: left;'>{platform_name}</td>
                        </tr>
                        <tr>
                            <td style='text-align: left; width: 100px;'>验证码:</td>
                            <td style='text-align: left;'>{code}</td>
                        </tr>
                        <tr>
                            <td style='text-align: left; width: 100px;'>剩余时间:</td>
                            <td style='text-align: left;'>{remaining} 秒</td>
                        </tr>
                    </table>
                """)
                self.current_code = code
            except Exception as e:
                self.code_label.setText(str(e))
                self.current_code = None
        else:
            self.current_code = None
    
    def copy_code(self):
        if hasattr(self, 'current_code') and self.current_code:
            # 复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_code)
            # 显示提示（可选）
            QMessageBox.information(self, "提示", "验证码已复制到剪贴板")
    
    # 添加新方法
    def show_context_menu(self, position):
        item = self.platform_list.itemAt(position)
        if item:
            context_menu = QMenu()
            delete_action = context_menu.addAction("删除")
            action = context_menu.exec_(self.platform_list.mapToGlobal(position))
            
            if action == delete_action:
                self.delete_platform(item.text())
    
    def delete_platform(self, platform_name):
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除平台 '{platform_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.totp_manager.remove_platform(platform_name)
                self.update_platform_list()
                self.code_label.setText("请选择平台")
            except Exception as e:
                QMessageBox.warning(self, "错误", str(e))
