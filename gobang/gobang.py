import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QMessageBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QPoint, QTimer, QPropertyAnimation
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush

class GobangGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.reset_game()

    def initUI(self):
        self.setWindowTitle("简易五子棋")
        self.setGeometry(100, 100, 800, 600)
        self.showMainMenu()

    def showMainMenu(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("简易五子棋")
        title_label.setStyleSheet("font-size: 36px; font-weight: bold; margin-bottom: 40px;")
        layout.addWidget(title_label)

        btn_double = QPushButton("双人对战模式")
        btn_double.setStyleSheet("font-size: 20px; padding: 10px 20px; margin: 10px;")
        btn_double.clicked.connect(self.start_double_player)
        layout.addWidget(btn_double)

        btn_ai = QPushButton("人机对战模式")
        btn_ai.setStyleSheet("font-size: 20px; padding: 10px 20px; margin: 10px;")
        btn_ai.clicked.connect(self.show_ai_selection)
        layout.addWidget(btn_ai)

        btn_rules = QPushButton("规则说明")
        btn_rules.setStyleSheet("font-size: 20px; padding: 10px 20px; margin: 10px;")
        btn_rules.clicked.connect(self.show_rules)
        layout.addWidget(btn_rules)

        self.setCentralWidget(central_widget)

    def show_ai_selection(self):
        # 创建自定义对话框
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle("选择先手")
        dialog.setFixedSize(300, 200)
        
        # 创建垂直布局
        layout = QVBoxLayout(dialog)
        
        # 添加提示文本
        label = QLabel("请选择您要执的棋子颜色：")
        label.setStyleSheet("font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(label)
        
        # 创建单选按钮
        self.rb_black = QRadioButton("黑棋（先手）")
        self.rb_white = QRadioButton("白棋（后手）")
        self.rb_black.setChecked(True)
        self.rb_black.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.rb_white.setStyleSheet("font-size: 14px; margin-bottom: 20px;")
        
        # 添加单选按钮到布局
        layout.addWidget(self.rb_black)
        layout.addWidget(self.rb_white)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("确定")
        btn_cancel = QPushButton("取消")
        
        # 设置按钮点击事件
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        
        # 添加按钮到按钮布局
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        
        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)
        
        # 执行对话框
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.player_color = 1 if self.rb_black.isChecked() else 2  # 1=黑，2=白
            self.start_ai_game()

    def show_rules(self):
        rules_text = """五子棋规则说明：

1. 棋盘规格：标准15×15路棋盘
2. 落子规则：
   - 点击棋盘落子点即可落子
   - 落子后不可移动或撤回
   - 同一落子点不可重复落子
   - 双人模式下，黑棋先手，黑白交替落子
3. 胜负判定：
   - 任意一方在横、竖、斜向形成连续5颗同色棋子，立即判定该方胜利
   - 棋盘填满且无胜负，判定为平局

祝您游戏愉快！"""
        QMessageBox.information(self, "规则说明", rules_text)

    def start_double_player(self):
        self.game_mode = "double"
        self.reset_game()
        self.showGameBoard()

    def start_ai_game(self):
        self.game_mode = "ai"
        self.reset_game()
        self.showGameBoard()
        
        # 如果AI先手（玩家选了白棋），AI先落子
        if self.current_player != self.player_color:
            self.ai_move()

    def showGameBoard(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # 回合提示
        self.turn_label = QLabel("当前回合：黑棋")
        self.turn_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.turn_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.turn_label)
        
        # 棋盘区域
        self.board_widget = BoardWidget(self)
        main_layout.addWidget(self.board_widget)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        btn_restart = QPushButton("重新开始")
        btn_restart.clicked.connect(self.confirm_restart)
        btn_back = QPushButton("返回主菜单")
        btn_back.clicked.connect(self.showMainMenu)
        control_layout.addWidget(btn_restart)
        control_layout.addWidget(btn_back)
        main_layout.addLayout(control_layout)
        
        self.setCentralWidget(central_widget)

    def reset_game(self):
        # 初始化棋盘，0=空，1=黑，2=白
        self.board = [[0 for _ in range(15)] for _ in range(15)]
        self.current_player = 1  # 1=黑，2=白，黑棋先手
        self.game_over = False
        
        # 重置胜利特效相关属性
        if hasattr(self, 'board_widget') and self.board_widget:
            self.board_widget.winning_pieces = []
            self.board_widget.victory_flash = 0
            self.board_widget.victory_flash_direction = 1
            self.board_widget.animating_pieces = {}

    def confirm_restart(self):
        # 创建自定义按钮的消息框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("确认重新开始")
        msg_box.setText("确定要重新开始游戏吗？")
        
        # 添加自定义按钮
        yes_btn = msg_box.addButton("确定", QMessageBox.ActionRole)
        no_btn = msg_box.addButton("取消", QMessageBox.ActionRole)
        
        # 设置默认按钮
        msg_box.setDefaultButton(no_btn)
        
        # 显示消息框
        msg_box.exec_()
        
        # 处理用户选择
        if msg_box.clickedButton() == yes_btn:
            self.reset_game()
            if self.game_mode == "ai" and self.current_player != self.player_color:
                self.ai_move()
            self.board_widget.update()
            self.update_turn_label()

    def update_turn_label(self):
        if not self.game_over:
            turn = "黑棋" if self.current_player == 1 else "白棋"
            self.turn_label.setText(f"当前回合：{turn}")

    def check_win(self, x, y):
        directions = [
            [(0, 1), (0, -1)],  # 横向
            [(1, 0), (-1, 0)],  # 纵向
            [(1, 1), (-1, -1)],  # 正斜向
            [(1, -1), (-1, 1)]   # 反斜向
        ]
        
        for direction in directions:
            count = 1
            winning_pieces = [(x, y)]  # 存储获胜的棋子位置
            for dx, dy in direction:
                nx, ny = x + dx, y + dy
                while 0 <= nx < 15 and 0 <= ny < 15 and self.board[nx][ny] == self.current_player:
                    count += 1
                    winning_pieces.append((nx, ny))
                    nx += dx
                    ny += dy
            if count >= 5:
                # 将获胜的棋子位置传递给BoardWidget
                self.board_widget.winning_pieces = winning_pieces
                # 开始胜利特效动画
                self.board_widget.animation_timer.start(20)
                return True
        return False

    def check_draw(self):
        for row in self.board:
            if 0 in row:
                return False
        return True

    def _evaluate_line(self, x, y, dx, dy, color):
        """评估某一方向上的棋型
        返回：
        - count: 连续的同色棋子数
        - blocks: 两端的阻挡数
        - empty_positions: 两端的空位
        - potential: 该方向上可能形成的最大连续数
        """
        # 先检查该位置是否可以落子
        if self.board[x][y] != 0:
            return 0, 2, [], 0
            
        # 临时放置棋子进行评估
        original = self.board[x][y]
        self.board[x][y] = color
        
        count = 1
        blocks = 0
        empty_positions = []
        potential = 1
        
        # 检查正方向
        nx, ny = x + dx, y + dy
        temp_count = 0
        while 0 <= nx < 15 and 0 <= ny < 15:
            if self.board[nx][ny] == color:
                temp_count += 1
                nx += dx
                ny += dy
            elif self.board[nx][ny] == 0:
                empty_positions.append((nx, ny))
                break
            else:
                blocks += 1
                break
        count += temp_count
        
        # 检查反方向
        nx, ny = x - dx, y - dy
        temp_count = 0
        while 0 <= nx < 15 and 0 <= ny < 15:
            if self.board[nx][ny] == color:
                temp_count += 1
                nx -= dx
                ny -= dy
            elif self.board[nx][ny] == 0:
                empty_positions.append((nx, ny))
                break
            else:
                blocks += 1
                break
        count += temp_count
        
        # 计算潜在的最大连续数（考虑可以延伸的空间）
        potential = count
        nx, ny = x + dx, y + dy
        while 0 <= nx < 15 and 0 <= ny < 15 and self.board[nx][ny] == 0:
            potential += 1
            nx += dx
            ny += dy
        nx, ny = x - dx, y - dy
        while 0 <= nx < 15 and 0 <= ny < 15 and self.board[nx][ny] == 0:
            potential += 1
            nx -= dx
            ny -= dy
        
        # 恢复原状态
        self.board[x][y] = original
        
        return count, blocks, empty_positions, potential
    
    def _detect_pattern(self, count, blocks, potential):
        """识别具体的棋型"""
        if count >= 5:
            return 'five'  # 连五
        elif count == 4:
            if blocks == 0:
                return 'open_four'  # 活四
            elif blocks == 1:
                return 'closed_four'  # 冲四
        elif count == 3:
            if blocks == 0:
                return 'open_three'  # 活三
            elif blocks == 1:
                return 'closed_three'  # 冲三
        elif count == 2:
            if blocks == 0 and potential >= 4:
                return 'open_two'  # 活二
            elif blocks == 1 and potential >= 4:
                return 'closed_two'  # 冲二
        
        return 'none'
    
    def _evaluate_position(self, x, y, color):
        """评估某个位置的落子价值"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        value = 0
        
        # 位置权重：中心区域权重更高
        center_distance = abs(x - 7) + abs(y - 7)
        position_weight = max(100 - center_distance * 10, 10)
        
        for dx, dy in directions:
            count, blocks, empty_positions, potential = self._evaluate_line(x, y, dx, dy, color)
            pattern = self._detect_pattern(count, blocks, potential)
            
            # 根据棋型分配权重
            if pattern == 'five':
                value += 1000000  # 连五，绝对优势
            elif pattern == 'open_four':
                value += 100000   # 活四，极大威胁
            elif pattern == 'closed_four':
                value += 50000    # 冲四，需要立即应对
            elif pattern == 'open_three':
                value += 10000    # 活三，很强的进攻手段
            elif pattern == 'closed_three':
                value += 5000     # 冲三，有威胁
            elif pattern == 'open_two':
                value += 1000     # 活二，进攻基础
            elif pattern == 'closed_two':
                value += 500      # 冲二，辅助进攻
            
            # 额外加分：如果该位置能同时形成多个棋型
            if count >= 2:
                value += count * 100
            
        # 考虑位置权重
        value += position_weight
        
        return value
    
    def ai_move(self):
        """智能AI落子"""
        # 找到所有空位置
        empty_positions = [(x, y) for x in range(15) for y in range(15) if self.board[x][y] == 0]
        if not empty_positions:
            return
        
        best_score = -1
        best_position = None
        
        # 评估每个空位置的落子价值
        for (x, y) in empty_positions:
            # 评估AI落子后的价值
            ai_score = self._evaluate_position(x, y, self.current_player)
            
            # 评估玩家落子后的价值（需要堵截）
            player_color = 1 if self.current_player == 2 else 2
            player_score = self._evaluate_position(x, y, player_color)
            
            # 总得分：优先考虑自己成五，其次堵截玩家成五
            # 根据游戏阶段调整策略：开局更注重自己的发展，中局均衡，残局更注重防守
            if sum(row.count(1) + row.count(2) for row in self.board) < 20:  # 开局
                total_score = ai_score * 3 + player_score
            elif sum(row.count(1) + row.count(2) for row in self.board) < 60:  # 中局
                total_score = ai_score * 2 + player_score
            else:  # 残局
                total_score = ai_score + player_score * 2
            
            # 额外加分：如果该位置能同时威胁多条线路
            ai_lines = 0
            player_lines = 0
            directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
            for dx, dy in directions:
                ai_count, ai_blocks, _, _ = self._evaluate_line(x, y, dx, dy, self.current_player)
                player_count, player_blocks, _, _ = self._evaluate_line(x, y, dx, dy, player_color)
                
                if ai_count >= 2:
                    ai_lines += 1
                if player_count >= 2:
                    player_lines += 1
            
            # 对于能同时形成多个活二、活三等棋型的位置给予额外奖励
            total_score += (ai_lines + player_lines) * 50
            
            if total_score > best_score:
                best_score = total_score
                best_position = (x, y)
            elif total_score == best_score and best_position:
                # 分数相同，优先选择靠近中心的位置
                current_center_dist = abs(x - 7) + abs(y - 7)
                best_center_dist = abs(best_position[0] - 7) + abs(best_position[1] - 7)
                if current_center_dist < best_center_dist:
                    best_position = (x, y)
        
        # 如果找到最佳位置，就落子
        if best_position:
            x, y = best_position
            self.board[x][y] = self.current_player
            # 开始落子动画
            self.board_widget.animating_pieces[(x, y)] = 0
            self.board_widget.animation_timer.start(30)
            self.board_widget.update()
            
            # 检查胜负
            if self.check_win(x, y):
                self.game_over = True
                self.show_win_message()
            else:
                self.switch_player()

    def switch_player(self):
        self.current_player = 2 if self.current_player == 1 else 1
        self.update_turn_label()
        
        # 如果是人机模式且轮到AI，AI落子
        if self.game_mode == "ai" and self.current_player != self.player_color:
            self.ai_move()

    def show_win_message(self):
        if self.game_over:
            if self.check_draw():
                winner = "平局"
            else:
                winner = "黑棋" if self.current_player == 1 else "白棋"
                if self.game_mode == "ai":
                    if self.current_player == self.player_color:
                        winner = "玩家"
                    else:
                        winner = "AI"
            
            message = f"游戏结束！{winner}获胜！"
            # 创建自定义按钮的消息框
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("游戏结束")
            msg_box.setText(message)
            
            # 添加自定义按钮
            restart_btn = msg_box.addButton("重新开始", QMessageBox.ActionRole)
            main_menu_btn = msg_box.addButton("返回主菜单", QMessageBox.ActionRole)
            
            # 显示消息框
            msg_box.exec_()
            
            # 处理用户选择
            if msg_box.clickedButton() == restart_btn:
                if self.game_mode == "double":
                    self.start_double_player()
                else:
                    self.start_ai_game()
            else:
                self.showMainMenu()

class BoardWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedSize(600, 600)
        self.grid_size = 40  # 网格间距
        self.margin = 20      # 边距
        
        # 动画相关属性
        self.animating_pieces = {}  # 存储正在动画的棋子 (x,y): animation_progress
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_speed = 10  # 动画速度
        
        # 胜利特效
        self.winning_pieces = []  # 存储获胜的棋子位置
        self.victory_flash = 0
        self.victory_flash_direction = 1

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制棋盘底色
        painter.setBrush(QColor(245, 222, 179))  # #F5DEB3
        painter.drawRect(0, 0, self.width(), self.height())
        
        # 绘制网格线
        painter.setPen(QColor(139, 69, 19))  # #8B4513
        for i in range(15):
            # 横线
            painter.drawLine(self.margin, self.margin + i * self.grid_size,
                            self.margin + 14 * self.grid_size, self.margin + i * self.grid_size)
            # 竖线
            painter.drawLine(self.margin + i * self.grid_size, self.margin,
                            self.margin + i * self.grid_size, self.margin + 14 * self.grid_size)
        
        # 绘制棋子
        for x in range(15):
            for y in range(15):
                color = self.parent.board[x][y]
                if color != 0:
                    cx = self.margin + x * self.grid_size
                    cy = self.margin + y * self.grid_size
                    radius = 18
                    
                    # 检查是否在动画中
                    if (x, y) in self.animating_pieces:
                        # 计算当前动画进度
                        progress = self.animating_pieces[(x, y)]
                        # 棋子从0%到100%缩放
                        current_radius = radius * (progress / 100)
                    else:
                        current_radius = radius
                    
                    if color == 1:  # 黑棋
                        painter.setBrush(QColor(0, 0, 0))
                        painter.drawEllipse(int(cx - current_radius), int(cy - current_radius), int(current_radius * 2), int(current_radius * 2))
                    else:  # 白棋
                        painter.setBrush(QColor(255, 255, 255))
                        painter.drawEllipse(int(cx - current_radius), int(cy - current_radius), int(current_radius * 2), int(current_radius * 2))
                        # 白棋描边
                        painter.setPen(QColor(192, 192, 192))
                        painter.drawEllipse(int(cx - current_radius), int(cy - current_radius), int(current_radius * 2), int(current_radius * 2))
                    
                    # 胜利特效
                    if (x, y) in self.winning_pieces and self.parent.game_over:
                        # 闪烁效果
                        flash_opacity = 255 - abs(255 - 2 * self.victory_flash)
                        if color == 1:
                            painter.setBrush(QColor(255, 100, 100, flash_opacity))
                        else:
                            painter.setBrush(QColor(100, 100, 255, flash_opacity))
                        painter.drawEllipse(int(cx - current_radius), int(cy - current_radius), int(current_radius * 2), int(current_radius * 2))

    def update_animation(self):
        # 更新所有动画棋子的进度
        for pos in list(self.animating_pieces.keys()):
            self.animating_pieces[pos] += self.animation_speed
            if self.animating_pieces[pos] >= 100:
                del self.animating_pieces[pos]
        
        # 更新胜利特效
        if self.parent.game_over and self.winning_pieces:
            # 更新闪烁效果
            self.victory_flash += 5 * self.victory_flash_direction
            if self.victory_flash >= 255 or self.victory_flash <= 0:
                self.victory_flash_direction *= -1
        
        if not self.animating_pieces and not (self.parent.game_over and self.winning_pieces):
            self.animation_timer.stop()
        
        self.update()
    
    def mousePressEvent(self, event):
        if self.parent.game_over:
            return
        
        # 检查是否是玩家回合
        if self.parent.game_mode == "ai" and self.parent.current_player != self.parent.player_color:
            return
        
        # 计算落子位置
        x = (event.x() - self.margin + self.grid_size // 2) // self.grid_size
        y = (event.y() - self.margin + self.grid_size // 2) // self.grid_size
        
        if 0 <= x < 15 and 0 <= y < 15 and self.parent.board[x][y] == 0:
            self.parent.board[x][y] = self.parent.current_player
            # 开始落子动画
            self.animating_pieces[(x, y)] = 0
            self.animation_timer.start(30)  # 30ms更新一次
            self.update()
            
            # 检查胜负
            if self.parent.check_win(x, y):
                self.parent.game_over = True
                self.parent.show_win_message()
            elif self.parent.check_draw():
                self.parent.game_over = True
                self.parent.show_win_message()
            else:
                self.parent.switch_player()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GobangGame()
    window.show()
    sys.exit(app.exec_())
