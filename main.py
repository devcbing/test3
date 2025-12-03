import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QMenuBar, QMenu, QDialog
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
                transform: scale(1.05);
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
        main_layout.addWidget(self.chess_board, 1)  # 设置拉伸因子为1，让棋盘填充剩余空间
        
    def new_game(self):
        """开始新游戏"""
        self.chess_board.init_board()
        self.current_turn_label.setText("当前出棋方: 红方")
        # 设置初始字体颜色为红色
        self.current_turn_label.setStyleSheet("QLabel { font-weight: bold; color: red; }")
        
    def ai_game(self):
        """切换到人机对战模式"""
        self.chess_board.set_game_mode("ai")
        self.new_game()
        QMessageBox.information(self, "提示", "已切换到人机对战模式")
        
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = ChineseChessGame()
    game.show()
    sys.exit(app.exec_())