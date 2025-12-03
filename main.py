import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QMenuBar, QMenu, QDialog, QComboBox, QDialogButtonBox
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QBrush
from chess_board import ChessBoard
from network_dialog import NetworkDialog

class VictoryDialog(QDialog):
    """自定义获胜弹窗"""
    def __init__(self, winner, parent=None):
        super().__init__(parent)
        self.setWindowTitle("游戏结束")
        self.setFixedSize(400, 250)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建背景部件
        background = QWidget()
        background.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 3px solid #FFD700;
            }
        """)
        
        # 创建内部布局
        inner_layout = QVBoxLayout(background)
        inner_layout.setAlignment(Qt.AlignCenter)
        inner_layout.setSpacing(20)
        
        # 胜利图标
        icon_label = QLabel()
        # 使用文本替代图标（可以根据需要替换为实际图标）
        icon_label.setText("🏆")
        icon_label.setFont(QFont("Arial", 60))
        icon_label.setAlignment(Qt.AlignCenter)
        inner_layout.addWidget(icon_label)
        
        # 胜利标题
        title_label = QLabel("恭喜获胜！")
        title_label.setFont(QFont("SimHei", 24, QFont.Bold))
        title_label.setStyleSheet("color: #FF6B6B;")
        title_label.setAlignment(Qt.AlignCenter)
        inner_layout.addWidget(title_label)
        
        # 获胜者信息
        winner_label = QLabel(f"{winner}获得了胜利！")
        winner_label.setFont(QFont("SimHei", 16))
        winner_label.setStyleSheet("color: #4ECDC4;")
        winner_label.setAlignment(Qt.AlignCenter)
        inner_layout.addWidget(winner_label)
        
        # 确定按钮
        ok_button = QPushButton("OK")
        ok_button.setFont(QFont("SimHei", 14))
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #333;
                border: none;
                border-radius: 15px;
                padding: 10px 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
            QPushButton:pressed {
                background-color: #FFA000;
            }
        """)
        ok_button.clicked.connect(self.accept)
        inner_layout.addWidget(ok_button)
        
        main_layout.addWidget(background)
        
        # 添加动画效果
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        self.animation.start()

class ChineseChessGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("中国象棋")
        
        # 设置合适的初始窗口大小，符合棋盘比例
        # 中国象棋棋盘比例：9列10行，宽度略小于高度
        # 理想比例：(9-1)/(10-1) ≈ 0.888
        self.setGeometry(100, 100, 800, 900)  # 宽度略小于高度
        
        self.initUI()
        
    def initUI(self):
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 所有菜单项直接添加到菜单栏
        
        # 人机对战菜单项
        ai_game_action = menubar.addAction("人机对战")
        ai_game_action.triggered.connect(self.ai_game)
        
        # 联机对战菜单项
        network_game_action = menubar.addAction("联机对战")
        network_game_action.triggered.connect(self.network_game)
        
        # 退出菜单项
        exit_action = menubar.addAction("退出")
        exit_action.triggered.connect(self.close)
        
        # 新游戏菜单项
        new_game_action = menubar.addAction("新游戏")
        new_game_action.triggered.connect(self.new_game)
        
        # 悔棋菜单项
        undo_action = menubar.addAction("悔棋")
        undo_action.triggered.connect(self.undo_move)
        
        # 认输菜单项
        resign_action = menubar.addAction("认输")
        resign_action.triggered.connect(self.resign)
        
        # 创建状态栏并添加当前出棋方提示
        self.statusBar()  # 初始化状态栏
        self.current_turn_label = QLabel("当前出棋方: 红方")
        self.current_turn_label.setStyleSheet("QLabel { font-weight: bold; color: #333; }")
        self.statusBar().addPermanentWidget(self.current_turn_label, 0)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局（垂直布局）
        main_layout = QVBoxLayout(central_widget)
        
        # 取消顶部控制面板（用户要求移除当前玩家显示栏）
        
        # 创建棋盘部件
        self.chess_board = ChessBoard(self)  # 设置父窗口为self
        # 设置游戏结束回调
        self.chess_board.game_over_callback = self.show_victory_dialog
        main_layout.addWidget(self.chess_board, 1)  # 设置拉伸因子为1，让棋盘填充剩余空间
        
    def new_game(self):
        """开始新游戏"""
        self.chess_board.init_board()
        self.current_turn_label.setText("当前出棋方: 红方")
        # 设置初始字体颜色为红色
        self.current_turn_label.setStyleSheet("QLabel { font-weight: bold; color: red; }")
        
    def ai_game(self):
        """切换到人机对战模式并选择难度"""
        # 创建难度选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("选择AI难度")
        dialog.setFixedSize(500, 450)  # 按比例缩小对话框尺寸
        
        # 设置对话框样式
        dialog.setStyleSheet(""".QDialog {
            background-color: #f0f0f0;
            border-radius: 15px;
        }
        
        QLabel {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            padding: 12px;
        }
        
        QComboBox {
            font-size: 16px;
            padding: 12px;
            margin: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            background-color: white;
        }
        
        QComboBox:hover {
            border-color: #aaa;
        }
        
        QComboBox:focus {
            border-color: #4CAF50;
            outline: none;
        }
        
        QPushButton {
            font-size: 20px;
            padding: 15px 30px;
            border-radius: 10px;
            margin: 15px;
            border: none;
        }
        
        QPushButton#okButton {
            background-color: #4CAF50;
            color: white;
            min-width: 100px;
            max-width: 100px;
            min-height: 40px;
            max-height: 40px;
            font-size: 16px;
            padding: 8px;
        }
        
        QPushButton#okButton:hover {
            background-color: #45a049;
        }
        
        QPushButton#cancelButton {
            background-color: #f44336;
            color: white;
            min-width: 100px;
            max-width: 100px;
            min-height: 40px;
            max-height: 40px;
            font-size: 16px;
            padding: 8px;
        }
        
        QPushButton#cancelButton:hover {
            background-color: #d32f2f;
        }""")
        
        layout = QVBoxLayout(dialog)
        
        # 添加标题标签
        title_label = QLabel("<center>选择AI难度等级</center>", dialog)
        title_label.setStyleSheet("QLabel { font-size: 18px; font-weight: bold; color: #4CAF50; padding: 15px; }")
        layout.addWidget(title_label)
        
        # 创建难度选择下拉框
        difficulty_combo = QComboBox(dialog)
        difficulty_combo.setFixedSize(300, 75)  # 增加下拉框高度
        difficulty_combo.setFont(QFont("SimHei", 14))  # 按比例缩小字体
        
        # 添加带有描述的难度等级
        difficulty_combo.addItem("简单 - 适合初学者")
        difficulty_combo.addItem("正常 - 平衡难度")
        difficulty_combo.addItem("困难 - 挑战策略")
        difficulty_combo.addItem("极难 - 高手对决")
        
        difficulty_combo.setCurrentIndex(1)  # 默认选择"正常"
        layout.addWidget(difficulty_combo, alignment=Qt.AlignCenter)
        layout.addSpacing(10)  # 增加间距
        
        # 添加难度说明
        self.difficulty_desc_label = QLabel("", dialog)
        self.difficulty_desc_label.setWordWrap(True)
        self.difficulty_desc_label.setMinimumHeight(100)  # 按比例缩小高度
        self.difficulty_desc_label.setFont(QFont("SimHei", 14))  # 按比例缩小字体
        self.difficulty_desc_label.setStyleSheet("QLabel { font-size: 14px; color: #333; padding: 15px; margin: 15px; background-color: #fff; border-radius: 10px; border: 2px solid #ddd; line-height: 1.5; }")
        layout.addWidget(self.difficulty_desc_label)
        
        # 创建按钮
        ok_button = QPushButton("确定", dialog)
        cancel_button = QPushButton("取消", dialog)
        
        # 设置按钮对象名，确保样式正确应用
        ok_button.setObjectName("okButton")
        cancel_button.setObjectName("cancelButton")
        
        # 设置按钮大小
        ok_button.setFixedSize(100, 40)
        cancel_button.setFixedSize(100, 40)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addSpacing(30)  # 按比例缩小按钮间距
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        layout.addSpacing(30)
        
        # 连接信号
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        difficulty_combo.currentIndexChanged.connect(self.update_difficulty_description)
        
        # 初始化难度描述
        self.update_difficulty_description(1)
        
        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            difficulty_map = {
                0: "simple",
                1: "normal",
                2: "hard",
                3: "expert"
            }
            selected_difficulty = difficulty_map[difficulty_combo.currentIndex()]
            difficulty_text = difficulty_combo.currentText().split(" - ")[0]
            
            # 设置游戏模式和AI难度
            self.chess_board.set_game_mode("ai")
            self.chess_board.set_ai_difficulty(selected_difficulty)
            self.new_game()
            
            # 创建更美观的提示信息
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("模式切换成功")
            msg_box.setText(f"已切换到人机对战模式")
            msg_box.setInformativeText(f"AI难度：{difficulty_text}")
            msg_box.setIcon(QMessageBox.Information)
            
            # 优化提示框样式
            msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 2px solid #e9ecef;
                padding: 20px;
                min-width: 350px;
            }
            
            QMessageBox::title {
                color: #495057;
                font-size: 18px;
                font-weight: bold;
                padding: 0 0 10px 0;
                text-align: center;
            }
            
            QMessageBox QLabel {
                color: #212529;
                font-size: 16px;
                padding: 8px;
                text-align: center;
                margin: 0 auto;
            }
            
            QMessageBox QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 14px;
                border: none;
                min-width: 100px;
                min-height: 36px;
                margin: 10px auto;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #0056b3;
            }
            
            QMessageBox QPushButton:pressed {
                background-color: #004085;
            }
            
            QMessageBox QGridLayout {
                alignment: Qt.AlignCenter;
            }
            
            QMessageBox QHBoxLayout {
                alignment: Qt.AlignCenter;
            }
            """)
            msg_box.exec_()
    
    def update_difficulty_description(self, index):
        """更新难度等级描述"""
        descriptions = {
            0: "简单难度：AI完全随机移动棋子，适合刚接触中国象棋的初学者熟悉规则。",
            1: "正常难度：AI会优先选择吃子或将军的移动，平衡了挑战性和可玩性。",
            2: "困难难度：AI会选择价值最高的移动，考虑吃子和将军策略，适合有一定基础的玩家。",
            3: "极难难度：AI会考虑多步走法，预测对手的反击，是对高手的终极挑战。"
        }
        self.difficulty_desc_label.setText(descriptions.get(index, ""))
        
    def network_game(self):
        """切换到联机对战模式"""
        # 打开网络对话框
        dialog = NetworkDialog(self)
        if dialog.exec_() == dialog.Accepted:
            is_server, ip, port = dialog.get_settings()
            
            # 初始化网络连接
            self.chess_board.init_network()
            
            if is_server:
                # 作为服务器启动
                self.chess_board.start_server(port)
            else:
                # 作为客户端连接
                self.chess_board.connect_to_server(ip, port)
            
            # 设置游戏模式
            self.chess_board.set_game_mode("network")
            self.new_game()
            QMessageBox.information(self, "提示", "已切换到联机对战模式")
        
    def undo_move(self):
        """悔棋"""
        if self.chess_board.undo_move():
            current_player = "红方" if self.chess_board.current_player == "red" else "黑方"
            color = "red" if self.chess_board.current_player == "red" else "black"
            self.current_turn_label.setText(f"当前出棋方: {current_player}")
            self.current_turn_label.setStyleSheet(f"QLabel {{ font-weight: bold; color: {color}; }}")
        else:
            QMessageBox.warning(self, "警告", "无法悔棋")
            
    def resign(self):
        """认输"""
        winner = "黑方" if self.chess_board.current_player == "red" else "红方"
        # 使用自定义获胜弹窗
        dialog = VictoryDialog(winner, self)
        dialog.exec_()
        self.new_game()
        
    def show_victory_dialog(self, winner):
        """显示获胜弹窗"""
        dialog = VictoryDialog(winner, self)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = ChineseChessGame()
    game.show()
    sys.exit(app.exec_())