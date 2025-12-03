from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup, QMessageBox
from PyQt5.QtCore import Qt

class NetworkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("局域网对战")
        self.setGeometry(300, 300, 400, 200)
        self.initUI()
        
    def initUI(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 模式选择
        mode_layout = QHBoxLayout()
        layout.addLayout(mode_layout)
        
        self.server_radio = QRadioButton("作为服务器")
        self.client_radio = QRadioButton("作为客户端")
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.server_radio)
        self.mode_group.addButton(self.client_radio)
        
        self.server_radio.setChecked(True)
        
        mode_layout.addWidget(self.server_radio)
        mode_layout.addWidget(self.client_radio)
        
        # 端口设置
        port_layout = QHBoxLayout()
        layout.addLayout(port_layout)
        
        port_label = QLabel("端口:")
        self.port_edit = QLineEdit("5555")
        
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_edit)
        
        # IP地址设置（客户端模式）
        ip_layout = QHBoxLayout()
        layout.addLayout(ip_layout)
        
        self.ip_label = QLabel("服务器IP:")
        self.ip_edit = QLineEdit("127.0.0.1")
        
        ip_layout.addWidget(self.ip_label)
        ip_layout.addWidget(self.ip_edit)
        
        # 按钮
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        # 连接信号
        self.server_radio.toggled.connect(self.toggle_mode)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        self.setLayout(layout)
        
    def toggle_mode(self, checked):
        """切换模式"""
        if checked:
            # 服务器模式
            self.ip_label.setEnabled(False)
            self.ip_edit.setEnabled(False)
        else:
            # 客户端模式
            self.ip_label.setEnabled(True)
            self.ip_edit.setEnabled(True)
    
    def get_settings(self):
        """获取设置"""
        is_server = self.server_radio.isChecked()
        port = int(self.port_edit.text())
        ip = self.ip_edit.text()
        
        return is_server, ip, port
