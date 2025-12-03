from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, QPolygonF
from PyQt5.QtCore import Qt, QPoint, QRect, QPropertyAnimation, QEasingCurve, QObject, pyqtProperty, QTimer
import random

class ChessBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_board()
        self.game_mode = "player"  # player, ai, network
        self.selected_piece = None
        self.selected_pos = None
        self.move_history = []
        
        # 爆炸特效相关属性
        self.explosions = []  # 存储当前所有爆炸效果
        self.explosion_timer = QTimer(self)
        self.explosion_timer.timeout.connect(self.update_explosions)
        self.explosion_timer.start(30)  # 每30毫秒更新一次爆炸效果
        
        # 庆祝特效相关
        self.celebration_effects = False  # 是否显示庆祝特效
        self.confetti = []  # 彩花粒子
        self.celebration_timer = QTimer(self)
        self.celebration_timer.timeout.connect(self.update_celebration)
        self.celebration_timer.start(30)
        
        # 将军提示特效相关
        self.check_effects = False  # 是否显示将军特效
        self.check_text = ""  # 将军提示文字
        self.check_alpha = 255  # 透明度
        self.check_pulse = 0  # 脉冲动画参数
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.update_check_effects)
        
        # 游戏结束回调函数
        self.game_over_callback = None
        
    def init_board(self):
        """初始化棋盘和棋子"""
        # 棋盘尺寸设置
        self.board_size = 9  # 9列
        self.row_count = 10  # 中国象棋标准棋盘有10行
        self.margin = 30
        
        # 初始化棋盘状态
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.row_count)]
        
        # 初始化棋子
        self.init_pieces()
        
        # 当前玩家
        self.current_player = "red"
        
        # 初始计算行间距
        self.resizeEvent(None)
        
    def init_pieces(self):
        """初始化棋子位置"""
        # 红方棋子（现在放在棋盘下方）
        red_pieces = [
            ("車", 9, 0), ("馬", 9, 1), ("象", 9, 2), ("士", 9, 3), ("将", 9, 4), ("士", 9, 5), ("象", 9, 6), ("馬", 9, 7), ("車", 9, 8),
            ("炮", 7, 1), ("炮", 7, 7),
            ("兵", 6, 0), ("兵", 6, 2), ("兵", 6, 4), ("兵", 6, 6), ("兵", 6, 8)
        ]
        
        # 黑方棋子（现在放在棋盘上方，与红方对称）
        black_pieces = [
            ("車", 0, 0), ("馬", 0, 1), ("象", 0, 2), ("士", 0, 3), ("将", 0, 4), ("士", 0, 5), ("象", 0, 6), ("馬", 0, 7), ("車", 0, 8),
            ("炮", 2, 1), ("炮", 2, 7),
            ("兵", 3, 0), ("兵", 3, 2), ("兵", 3, 4), ("兵", 3, 6), ("兵", 3, 8)
        ]
        
        # 放置红方棋子
        for name, row, col in red_pieces:
            self.board[row][col] = {"name": name, "color": "red", "row": row, "col": col}
        
        # 放置黑方棋子
        for name, row, col in black_pieces:
            self.board[row][col] = {"name": name, "color": "black", "row": row, "col": col}
    
    def set_game_mode(self, mode):
        """设置游戏模式"""
        self.game_mode = mode
    
    def resizeEvent(self, event):
        """重写调整大小事件，根据窗口大小动态计算行间距并保持正确比例"""
        # 中国象棋棋盘标准比例：9列10行，宽度略小于高度
        # 计算理想比例：宽度/高度 = (9-1)/(10-1) ≈ 0.888
        ideal_ratio = (self.board_size - 1) / (self.row_count - 1)
        
        # 获取当前窗口比例
        current_ratio = self.width() / self.height() if self.height() > 0 else ideal_ratio
        
        # 计算棋子最大半径（棋子大小的一半），用于调整边距
        max_piece_radius = 40  # 最大棋子半径
        
        # 根据比例调整行间距，确保棋盘保持正确比例，同时考虑棋子大小避免边缘遮挡
        if current_ratio > ideal_ratio:
            # 窗口太宽，以高度为基准计算
            # 增加更多边距，确保上下边缘的棋子不会被窗口遮挡
            available_height = self.height() - max_piece_radius * 2  # 留足够边距容纳棋子
            self.line_spacing = int(available_height / (self.row_count - 1))
        else:
            # 窗口太高或比例合适，以宽度为基准计算
            available_width = self.width() - max_piece_radius * 2  # 留足够边距
            self.line_spacing = int(available_width / (self.board_size - 1))
        
        # 确保行间距至少为30，避免棋子太小
        self.line_spacing = max(self.line_spacing, 30)
        
        # 调用父类的resizeEvent
        super().resizeEvent(event)
        
        # 重绘棋盘
        self.update()
    
    def paintEvent(self, event):
        """绘制棋盘和棋子"""
        painter = QPainter(self)
        
        # 设置抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 计算棋盘实际绘制区域
        board_width = (self.board_size - 1) * self.line_spacing
        board_height = (self.row_count - 1) * self.line_spacing
        
        # 计算棋盘左上角坐标，使其居中
        board_x = (self.width() - board_width) // 2
        board_y = (self.height() - board_height) // 2
        
        # 绘制棋盘背景
        original_color = QColor(222, 184, 135)  # 原始棋盘颜色
        painter.fillRect(self.rect(), original_color)
        
        # 只改变楚河汉界对应位置的背景，使用海水颜色，只显示一行
        river_color = QColor(135, 206, 235)  # 海水颜色
        painter.fillRect(
            int(board_x), int(board_y + 4 * self.line_spacing),
            int(board_width), int(self.line_spacing),
            river_color
        )
        
        # 移除棋子位置的原始颜色圆形，因为现在只改变楚河汉界区域的背景
        
        # 绘制棋盘线条
        self.draw_board_lines(painter, board_x, board_y)
        
        # 绘制棋子
        self.draw_pieces(painter, board_x, board_y)
        
        # 绘制将军特效
        self.draw_check_effects(painter)
        
    def draw_board_lines(self, painter, board_x, board_y):
        """绘制棋盘线条"""
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)
        
        # 绘制横线
        for i in range(10):  # 中国象棋标准棋盘应该有10条横线
            y = board_y + i * self.line_spacing
            painter.drawLine(int(board_x), int(y), int(board_x + (self.board_size - 1) * self.line_spacing), int(y))
        
        # 绘制竖线
        for i in range(self.board_size):
            x = board_x + i * self.line_spacing
            painter.drawLine(int(x), int(board_y), int(x), int(board_y + (self.row_count - 1) * self.line_spacing))
        
        # 绘制河界（楚河汉界）
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        # 绘制河界横线
        painter.drawLine(int(board_x), int(board_y + 4 * self.line_spacing), 
                        int(board_x + 8 * self.line_spacing), int(board_y + 4 * self.line_spacing))
        painter.drawLine(int(board_x), int(board_y + 5 * self.line_spacing), 
                        int(board_x + 8 * self.line_spacing), int(board_y + 5 * self.line_spacing))
        
        # 绘制楚河汉界文字，确保位置居中
        font = QFont("SimHei", 18, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255), 3))  # 白色文字带阴影效果
        
        # 楚河位置（左侧）
        painter.drawText(
            int(board_x + 1.5 * self.line_spacing), 
            int(board_y + 4.5 * self.line_spacing + 5), 
            "楚河"
        )
        
        # 汉界位置（右侧）
        painter.drawText(
            int(board_x + 5.5 * self.line_spacing), 
            int(board_y + 4.5 * self.line_spacing + 5), 
            "汉界"
        )
        
        # 绘制九宫
        # 红方九宫（现在在底部）
        painter.drawLine(int(board_x + 3 * self.line_spacing), int(board_y + 9 * self.line_spacing), 
                        int(board_x + 5 * self.line_spacing), int(board_y + 7 * self.line_spacing))
        painter.drawLine(int(board_x + 5 * self.line_spacing), int(board_y + 9 * self.line_spacing), 
                        int(board_x + 3 * self.line_spacing), int(board_y + 7 * self.line_spacing))
        
        # 黑方九宫（现在在顶部）
        painter.drawLine(int(board_x + 3 * self.line_spacing), int(board_y), 
                        int(board_x + 5 * self.line_spacing), int(board_y + 2 * self.line_spacing))
        painter.drawLine(int(board_x + 5 * self.line_spacing), int(board_y), 
                        int(board_x + 3 * self.line_spacing), int(board_y + 2 * self.line_spacing))
    
    def add_explosion(self, x, y, color):
        """添加爆炸特效"""
        explosion = {
            "x": x,
            "y": y,
            "color": color,
            "radius": 0,
            "max_radius": int(self.line_spacing * 1.5),  # 爆炸最大半径为棋子大小的1.5倍
            "alpha": 255,
            "particles": []  # 爆炸粒子
        }
        
        # 创建爆炸粒子
        particle_count = 12
        for i in range(particle_count):
            angle = (i / particle_count) * 360
            particle = {
                "x": x,
                "y": y,
                "angle": angle,
                "speed": (self.line_spacing / 20) + (i % 5) * (self.line_spacing / 50),  # 随机速度
                "size": int(self.line_spacing / 15) + (i % 3),  # 随机大小
                "alpha": 255
            }
            explosion["particles"].append(particle)
        
        self.explosions.append(explosion)
    
    def update_explosions(self):
        """更新爆炸特效"""
        for explosion in self.explosions[:]:
            # 更新爆炸半径
            explosion["radius"] += self.line_spacing / 20
            
            # 更新透明度
            explosion["alpha"] -= 15
            
            # 更新粒子
            for particle in explosion["particles"]:
                from math import radians, cos, sin
                particle["x"] += cos(radians(particle["angle"])) * particle["speed"]
                particle["y"] += sin(radians(particle["angle"])) * particle["speed"]
                particle["alpha"] -= 10
                
            # 移除结束的爆炸
            if explosion["alpha"] <= 0:
                self.explosions.remove(explosion)
        
        # 如果有爆炸效果，重绘棋盘
        if self.explosions:
            self.update()
            
    def start_celebration(self):
        """开始庆祝特效"""
        self.celebration_effects = True
        # 生成大量彩花粒子
        self.confetti = []
        for _ in range(200):  # 生成200个彩花粒子
            # 随机位置（在棋盘范围内）
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            # 随机颜色
            colors = [
                (255, 0, 0), (0, 255, 0), (0, 0, 255),  # 红、绿、蓝
                (255, 255, 0), (255, 0, 255), (0, 255, 255),  # 黄、紫、青
                (255, 165, 0), (255, 192, 203), (128, 0, 128)   # 橙、粉、紫
            ]
            color = random.choice(colors)
            # 随机大小
            size = random.randint(3, 8)
            # 随机速度和角度
            speed = random.uniform(1, 4)
            angle = random.uniform(0, 360)
            # 添加彩花粒子
            self.confetti.append({
                "x": x,
                "y": y,
                "color": color,
                "size": size,
                "speed": speed,
                "angle": angle,
                "alpha": 255,
                "rotation": random.uniform(0, 360),
                "rotation_speed": random.uniform(-2, 2)
            })
            
    def update_celebration(self):
        """更新庆祝特效"""
        if not self.celebration_effects:
            return
            
        for confetti in self.confetti[:]:
            # 更新位置
            from math import radians, cos, sin
            confetti["x"] += cos(radians(confetti["angle"])) * confetti["speed"]
            confetti["y"] += sin(radians(confetti["angle"])) * confetti["speed"]
            # 添加重力效果
            confetti["y"] += 0.5
            # 更新旋转
            confetti["rotation"] += confetti["rotation_speed"]
            # 更新透明度
            confetti["alpha"] -= 2
            
            # 移除超出屏幕或透明度为0的彩花
            if (confetti["x"] < -50 or confetti["x"] > self.width() + 50 or 
                confetti["y"] < -50 or confetti["y"] > self.height() + 50 or 
                confetti["alpha"] <= 0):
                self.confetti.remove(confetti)
        
        # 如果所有彩花消失，结束庆祝
        if not self.confetti:
            self.celebration_effects = False
        else:
            self.update()
    
    def draw_explosions(self, painter):
        """绘制爆炸特效"""
        for explosion in self.explosions:
            # 绘制爆炸外圈
            if explosion["alpha"] > 0:
                # 根据棋子颜色设置爆炸颜色
                if explosion["color"] == "red":
                    explosion_color = QColor(255, 80, 80, explosion["alpha"])
                else:
                    explosion_color = QColor(80, 80, 80, explosion["alpha"])
                
                # 绘制爆炸圆圈
                brush = QBrush(explosion_color)
                painter.setBrush(brush)
                painter.setPen(QPen(Qt.NoPen))
                painter.drawEllipse(int(explosion["x"] - explosion["radius"]),
                                   int(explosion["y"] - explosion["radius"]),
                                   int(explosion["radius"] * 2),
                                   int(explosion["radius"] * 2))
                
                # 绘制爆炸粒子
                for particle in explosion["particles"]:
                    if particle["alpha"] > 0:
                        particle_color = QColor(255, 200, 0, particle["alpha"])  # 粒子使用黄色
                        brush = QBrush(particle_color)
                        painter.setBrush(brush)
                        painter.drawEllipse(int(particle["x"] - particle["size"]),
                                           int(particle["y"] - particle["size"]),
                                           int(particle["size"] * 2),
                                           int(particle["size"] * 2))
    
    def draw_pieces(self, painter, board_x, board_y):
        """绘制棋子"""
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece:
                    self.draw_piece(painter, piece, row, col, board_x, board_y)
        
        # 绘制爆炸特效
        self.draw_explosions(painter)
        
        # 绘制庆祝特效
        self.draw_celebration(painter)
        
    def draw_celebration(self, painter):
        """绘制庆祝特效"""
        if not self.celebration_effects:
            return
            
        for confetti in self.confetti:
            # 保存当前绘图状态
            painter.save()
            
            # 设置透明度
            color = QColor(*confetti["color"], confetti["alpha"])
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 1))
            
            # 移动到彩花位置
            painter.translate(confetti["x"], confetti["y"])
            
            # 旋转彩花
            painter.rotate(confetti["rotation"])
            
            # 绘制彩花（作为旋转的矩形）
            size = confetti["size"]
            # 将浮点数转换为整数
            painter.drawRect(int(-size/2), int(-size/2), int(size), int(size))
            
            # 恢复绘图状态
            painter.restore()
    
    def draw_piece(self, painter, piece, row, col, board_x, board_y):
        """绘制单个棋子"""
        x = board_x + col * self.line_spacing
        y = board_y + row * self.line_spacing
        
        # 棋子大小随棋盘大小变化，设置为行间距的85%，使棋子之间有适当间距
        piece_size = int(self.line_spacing * 0.85)
        
        # 绘制选中效果
        if (row, col) == self.selected_pos:
            # 增强选中特效：多层发光边框 + 强内部高亮
            
            # 1. 最外层大发光边框（亮黄色）
            glow_pen_outer = QPen(QColor(255, 255, 0), 8, Qt.SolidLine)
            painter.setPen(glow_pen_outer)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - piece_size // 2 - 4, y - piece_size // 2 - 4, 
                               piece_size + 8, piece_size + 8)
            
            # 2. 中层发光边框（亮橙色）
            glow_pen_middle = QPen(QColor(255, 165, 0), 6, Qt.SolidLine)
            painter.setPen(glow_pen_middle)
            painter.drawEllipse(x - piece_size // 2 - 2, y - piece_size // 2 - 2, 
                               piece_size + 4, piece_size + 4)
            
            # 3. 内部高亮效果（强金色）
            highlight_brush = QBrush(QColor(255, 215, 0, 220))  # 提高不透明度
            painter.setBrush(highlight_brush)
            painter.setPen(QPen(QColor(255, 140, 0), 4))  # 加粗边框
            painter.drawEllipse(x - piece_size // 2, y - piece_size // 2, 
                               piece_size, piece_size)
        
        # 绘制棋子圆圈
        if piece["color"] == "red":
            # 红方棋子使用红色渐变
            gradient = QRadialGradient(x, y, piece_size // 2, x - piece_size // 5, y - piece_size // 5)
            gradient.setColorAt(0, QColor(255, 140, 120))
            gradient.setColorAt(1, QColor(220, 50, 30))
            painter.setBrush(gradient)
        else:
            # 黑方棋子使用黑色渐变
            gradient = QRadialGradient(x, y, piece_size // 2, x - piece_size // 5, y - piece_size // 5)
            gradient.setColorAt(0, QColor(160, 160, 160))
            gradient.setColorAt(1, QColor(40, 40, 40))
            painter.setBrush(gradient)
        
        # 绘制棋子轮廓
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(x - piece_size // 2, y - piece_size // 2, 
                           piece_size, piece_size)
        
        # 绘制棋子文字（字体大小随棋子大小变化）
        font_size = int(piece_size * 0.4)  # 字体大小为棋子大小的40%，进一步减小确保在圆形内部
        font = QFont("SimHei", font_size, QFont.Normal)  # 移除加粗效果
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        
        # 创建一个与棋子大小相同的矩形区域
        text_rect = QRect(x - piece_size // 2, y - piece_size // 2, piece_size, piece_size)
        # 使用Qt的对齐功能让文字在矩形内居中显示
        painter.drawText(text_rect, Qt.AlignCenter, piece["name"])
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if self.game_mode == "ai" and self.current_player == "black":
            return  # 人机对战时黑方由AI控制
        
        # 计算棋盘实际绘制区域
        board_width = (self.board_size - 1) * self.line_spacing
        board_height = (self.row_count - 1) * self.line_spacing
        
        # 计算棋盘左上角坐标，与paintEvent保持一致
        board_x = (self.width() - board_width) // 2
        board_y = (self.height() - board_height) // 2
        
        # 计算点击位置对应的棋盘坐标
        col = (event.x() - board_x + self.line_spacing // 2) // self.line_spacing
        row = (event.y() - board_y + self.line_spacing // 2) // self.line_spacing
        
        # 检查坐标是否在棋盘范围内
        if 0 <= col < self.board_size and 0 <= row < self.row_count:
            piece = self.board[row][col]
            
            if self.selected_piece:
                # 如果已经选中了棋子，尝试移动
                if self.can_move(self.selected_pos[0], self.selected_pos[1], row, col):
                    # 执行移动
                    self.move_piece(self.selected_pos[0], self.selected_pos[1], row, col)
                    self.selected_piece = None
                    self.selected_pos = None
                    
                    # 检查游戏是否结束
                    if self.is_game_over():
                        # 开始庆祝特效
                        self.start_celebration()
                        winner = self.get_winner()
                        # 使用回调函数显示游戏结束信息
                        if self.game_over_callback:
                            self.game_over_callback(winner)
                        else:
                            QMessageBox.information(self, "游戏结束", f"{winner}获胜！")
                        return
                    
                    # 切换玩家
                    self.switch_player()
                    
                    # 如果是人机对战且轮到黑方
                    if self.game_mode == "ai" and self.current_player == "black":
                        self.ai_move()
                else:
                    # 如果点击的是自己的棋子，重新选择
                    if piece and piece["color"] == self.current_player:
                        self.selected_piece = piece
                        self.selected_pos = (row, col)
                    else:
                        # 取消选择
                        self.selected_piece = None
                        self.selected_pos = None
            else:
                # 如果没有选中棋子，尝试选择
                if piece and piece["color"] == self.current_player:
                    self.selected_piece = piece
                    self.selected_pos = (row, col)
            
            # 重绘棋盘
            self.update()
    
    def can_move(self, from_row, from_col, to_row, to_col):
        """检查棋子是否可以移动到目标位置"""
        # 检查目标位置是否有己方棋子
        if self.board[to_row][to_col] and self.board[to_row][to_col]["color"] == self.current_player:
            return False
        
        piece = self.board[from_row][from_col]
        
        # 根据棋子类型检查移动规则
        if piece["name"] == "将" or piece["name"] == "帅":
            return self.can_move_jiang(from_row, from_col, to_row, to_col)
        elif piece["name"] == "士":
            return self.can_move_shi(from_row, from_col, to_row, to_col)
        elif piece["name"] == "象" or piece["name"] == "相":
            return self.can_move_xiang(from_row, from_col, to_row, to_col)
        elif piece["name"] == "馬":
            return self.can_move_ma(from_row, from_col, to_row, to_col)
        elif piece["name"] == "車":
            return self.can_move_ju(from_row, from_col, to_row, to_col)
        elif piece["name"] == "炮":
            return self.can_move_pao(from_row, from_col, to_row, to_col)
        elif piece["name"] == "兵" or piece["name"] == "卒":
            return self.can_move_bing(from_row, from_col, to_row, to_col)
        
        return False
    
    def can_move_jiang(self, from_row, from_col, to_row, to_col):
        """检查将/帅的移动规则"""
        piece = self.board[from_row][from_col]
        # 检查是否在九宫内（红方现在在下方）
        if piece["color"] == "red":
            # 红方九宫在下方（第7-9行）
            if not (7 <= to_row <= 9 and 3 <= to_col <= 5):
                return False
        else:
            # 黑方九宫在上方（第0-2行）
            if not (0 <= to_row <= 2 and 3 <= to_col <= 5):
                return False
        
        # 只能走一步
        if abs(to_row - from_row) + abs(to_col - from_col) != 1:
            return False
        
        return True
    
    def can_move_shi(self, from_row, from_col, to_row, to_col):
        """检查士的移动规则"""
        piece = self.board[from_row][from_col]
        # 检查是否在九宫内（红方现在在下方）
        if piece["color"] == "red":
            # 红方九宫在下方（第7-9行）
            if not (7 <= to_row <= 9 and 3 <= to_col <= 5):
                return False
        else:
            # 黑方九宫在上方（第0-2行）
            if not (0 <= to_row <= 2 and 3 <= to_col <= 5):
                return False
        
        # 只能走斜线一步
        if abs(to_row - from_row) != 1 or abs(to_col - from_col) != 1:
            return False
        
        return True
    
    def can_move_xiang(self, from_row, from_col, to_row, to_col):
        """检查象/相的移动规则"""
        piece = self.board[from_row][from_col]
        # 检查是否过河（红方现在在下方）
        if piece["color"] == "red":
            # 红方不能过河到上方
            if to_row < 5:
                return False
        else:
            # 黑方不能过河到下方
            if to_row > 4:
                return False
        
        # 只能走田字
        if abs(to_row - from_row) != 2 or abs(to_col - from_col) != 2:
            return False
        
        # 检查田字中心是否有棋子
        center_row = (from_row + to_row) // 2
        center_col = (from_col + to_col) // 2
        if self.board[center_row][center_col]:
            return False
        
        return True
    
    def can_move_ma(self, from_row, from_col, to_row, to_col):
        """检查马的移动规则"""
        # 检查是否走日字
        dx = abs(to_col - from_col)
        dy = abs(to_row - from_row)
        if not ((dx == 1 and dy == 2) or (dx == 2 and dy == 1)):
            return False
        
        # 检查马脚是否被绊
        if dx == 1 and dy == 2:
            # 横向移动1，纵向移动2
            if to_row > from_row:
                # 向下移动
                if self.board[from_row + 1][from_col]:
                    return False
            else:
                # 向上移动
                if self.board[from_row - 1][from_col]:
                    return False
        else:
            # 横向移动2，纵向移动1
            if to_col > from_col:
                # 向右移动
                if self.board[from_row][from_col + 1]:
                    return False
            else:
                # 向左移动
                if self.board[from_row][from_col - 1]:
                    return False
        
        return True
    
    def can_move_ju(self, from_row, from_col, to_row, to_col):
        """检查车的移动规则"""
        # 必须是直线移动
        if from_row != to_row and from_col != to_col:
            return False
        
        # 检查路径是否有棋子阻挡
        if from_row == to_row:
            # 横向移动
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if self.board[from_row][col]:
                    return False
        else:
            # 纵向移动
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if self.board[row][from_col]:
                    return False
        
        return True
    
    def can_move_pao(self, from_row, from_col, to_row, to_col):
        """检查炮的移动规则"""
        # 必须是直线移动
        if from_row != to_row and from_col != to_col:
            return False
        
        # 计算中间的棋子数量
        piece_count = 0
        if from_row == to_row:
            # 横向移动
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if self.board[from_row][col]:
                    piece_count += 1
        else:
            # 纵向移动
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if self.board[row][from_col]:
                    piece_count += 1
        
        # 炮吃子时需要中间有一个棋子，移动时中间不能有棋子
        if self.board[to_row][to_col]:
            # 吃子
            return piece_count == 1
        else:
            # 移动
            return piece_count == 0
    
    def can_move_bing(self, from_row, from_col, to_row, to_col):
        """检查兵/卒的移动规则"""
        piece = self.board[from_row][from_col]
        # 确定移动方向（红方现在在下方，应该向上移动）
        direction = -1 if piece["color"] == "red" else 1
        
        # 检查是否过河
        crossed_river = False
        if piece["color"] == "red" and from_row <= 4:
            crossed_river = True
        if piece["color"] == "black" and from_row >= 5:
            crossed_river = True
        
        # 未过河只能向前
        if not crossed_river:
            if to_col != from_col or (to_row - from_row) != direction:
                return False
        else:
            # 过河后可以向前或左右
            if (to_row - from_row) == direction and to_col == from_col:
                return True
            elif to_row == from_row and abs(to_col - from_col) == 1:
                return True
            else:
                return False
        
        return True
    
    def move_piece(self, from_row, from_col, to_row, to_col):
        """移动棋子"""
        # 记录移动历史
        captured_piece = self.board[to_row][to_col]
        self.move_history.append((from_row, from_col, to_row, to_col, captured_piece))
        
        # 如果有吃棋，添加爆炸特效
        if captured_piece:
            # 计算爆炸中心位置
            board_width = (self.board_size - 1) * self.line_spacing
            board_height = (self.row_count - 1) * self.line_spacing
            board_x = (self.width() - board_width) // 2
            board_y = (self.height() - board_height) // 2
            
            explosion_x = board_x + to_col * self.line_spacing
            explosion_y = board_y + to_row * self.line_spacing
            
            # 添加爆炸效果
            self.add_explosion(explosion_x, explosion_y, captured_piece["color"])
        
        # 执行移动
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        
        # 检查对方是否被将军
        enemy_color = "black" if self.current_player == "red" else "red"
        if self.is_checked(enemy_color):
            self.show_check_effect(enemy_color)
        
        # 如果是局域网对战，发送移动数据
        if self.game_mode == "network" and self.is_connected:
            self.send_move(from_row, from_col, to_row, to_col)
    
    def switch_player(self):
        """切换玩家"""
        # 切换玩家
        self.current_player = "black" if self.current_player == "red" else "red"
        player_name = self.get_player_name()
        
        # 获取真正的主窗口实例（通过父窗口的父窗口）
        main_window = self.parent().parent() if self.parent() else None
        if main_window:
            # 更新当前出棋方提示
            main_window.current_turn_label.setText(f"当前出棋方: {player_name}")
            # 根据当前玩家设置字体颜色
            color = "red" if self.current_player == "red" else "black"
            main_window.current_turn_label.setStyleSheet(f"QLabel {{ font-weight: bold; color: {color}; }}")
        
        # 检查当前玩家是否被将军
        if self.is_checked(self.current_player):
            self.show_check_effect(self.current_player)
    
    def get_player_name(self):
        """获取当前玩家名称"""
        return "红方" if self.current_player == "red" else "黑方"
    
    def is_game_over(self):
        """检查游戏是否结束"""
        # 检查是否有一方的将/帅被吃掉
        red_jiang = False
        black_jiang = False
        
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece:
                    if (piece["name"] == "将" or piece["name"] == "帅") and piece["color"] == "red":
                        red_jiang = True
                    elif (piece["name"] == "将" or piece["name"] == "帅") and piece["color"] == "black":
                        black_jiang = True
        
        return not red_jiang or not black_jiang
    
    def is_checked(self, color):
        """检查指定颜色的玩家是否被将军"""
        # 找到当前颜色的将/帅
        jiang_pos = None
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece and (piece["name"] == "将" or piece["name"] == "帅") and piece["color"] == color:
                    jiang_pos = (row, col)
                    break
            if jiang_pos:
                break
        
        if not jiang_pos:
            return False
        
        # 检查对方是否有棋子可以攻击到将/帅
        enemy_color = "black" if color == "red" else "red"
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece and piece["color"] == enemy_color:
                    if self.can_move(row, col, jiang_pos[0], jiang_pos[1]):
                        return True
        
        return False
    
    def show_check_effect(self, color):
        """显示将军特效"""
        self.check_effects = True
        self.check_text = "红方被将军！" if color == "red" else "黑方被将军！"
        self.check_alpha = 255
        self.check_pulse = 0
        if not self.check_timer.isActive():
            self.check_timer.start(50)  # 每50毫秒更新一次
    
    def update_check_effects(self):
        """更新将军特效"""
        # 更新脉冲动画（加快爆炸速度）
        self.check_pulse += 0.2
        if self.check_pulse > 1:
            self.check_pulse = 1
        
        # 快速降低透明度
        if self.check_alpha > 0:
            self.check_alpha -= 8  # 加快消失速度
            if self.check_alpha < 0:
                self.check_alpha = 0
        else:
            self.check_effects = False
            self.check_timer.stop()
        
        self.update()
    
    def draw_check_effects(self, painter):
        """绘制将军特效（爆炸弹出效果）"""
        if not self.check_effects:
            return
        
        # 设置透明度
        painter.save()
        
        # 计算棋盘实际绘制区域
        board_width = (self.board_size - 1) * self.line_spacing
        board_height = (self.row_count - 1) * self.line_spacing
        board_x = (self.width() - board_width) // 2
        board_y = (self.height() - board_height) // 2
        
        # 计算棋盘中心位置
        center_x = board_x + board_width // 2
        center_y = board_y + board_height // 2
        
        # 绘制爆炸动画效果（向外扩散的圆形）
        explosion_radius = int(self.line_spacing * 2 * (0.5 + self.check_pulse * 0.5))  # 最大半径为两个格子
        explosion_color = QColor(255, 0, 0, int(self.check_alpha * 0.5))
        painter.setBrush(QBrush(explosion_color))
        painter.setPen(QPen(QColor(255, 0, 0, self.check_alpha), 2))
        painter.drawEllipse(int(center_x - explosion_radius), int(center_y - explosion_radius), 
                          int(explosion_radius * 2), int(explosion_radius * 2))
        
        # 绘制将军文字（爆炸弹出效果）
        font_size = 36 + int(12 * self.check_pulse)  # 文字大小随爆炸变化
        font = QFont("SimHei", font_size, QFont.Bold)
        painter.setFont(font)
        
        # 设置文字颜色和透明度
        text_color = QColor(255, 0, 0, self.check_alpha)
        painter.setPen(QPen(text_color, 2))
        
        # 计算文字位置（居中）
        text_rect = painter.fontMetrics().boundingRect(self.check_text)
        x = center_x - text_rect.width() // 2
        y = center_y + text_rect.height() // 2
        
        # 添加文字阴影效果
        shadow_color = QColor(0, 0, 0, int(self.check_alpha * 0.3))
        painter.setPen(QPen(shadow_color, 2))
        painter.drawText(int(x + 2), int(y + 2), self.check_text)
        
        # 绘制主文字
        painter.setPen(QPen(text_color, 2))
        painter.drawText(int(x), int(y), self.check_text)
        
        painter.restore()
    
    def get_winner(self):
        """获取获胜者"""
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece and (piece["name"] == "将" or piece["name"] == "帅"):
                    return "红方" if piece["color"] == "red" else "黑方"
        return ""
    
    def undo_move(self):
        """悔棋"""
        if not self.move_history:
            return False
        
        # 取出最后一步
        from_row, from_col, to_row, to_col, captured_piece = self.move_history.pop()
        
        # 恢复棋子
        self.board[from_row][from_col] = self.board[to_row][to_col]
        self.board[to_row][to_col] = captured_piece
        
        # 切换玩家
        self.switch_player()
        
        # 重绘棋盘
        self.update()
        
        return True
    
    def ai_move(self):
        """AI移动（简单实现）"""
        # 简单的AI实现：随机选择一个可移动的棋子并移动
        import random
        
        # 收集所有可移动的棋子
        movable_pieces = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece and piece["color"] == "black":
                    # 收集所有可能的移动
                    for to_row in range(len(self.board)):
                        for to_col in range(len(self.board[to_row])):
                            if self.can_move(row, col, to_row, to_col):
                                movable_pieces.append((row, col, to_row, to_col))
        
        if movable_pieces:
            # 随机选择一个移动
            from_row, from_col, to_row, to_col = random.choice(movable_pieces)
            
            # 执行移动
            self.move_piece(from_row, from_col, to_row, to_col)
            
            # 检查游戏是否结束
            if self.is_game_over():
                # 开始庆祝特效
                self.start_celebration()
                winner = self.get_winner()
                # 使用回调函数显示游戏结束信息
                if self.game_over_callback:
                    self.game_over_callback(winner)
                else:
                    QMessageBox.information(self, "游戏结束", f"{winner}获胜！")
                return
            
            # 切换玩家
            self.switch_player()
            
            # 重绘棋盘
            self.update()
    
    def init_network(self):
        """初始化网络连接"""
        import socket
        import threading
        
        self.socket = None
        self.is_server = False
        self.is_connected = False
    
    def start_server(self, port=5555):
        """启动服务器"""
        import socket
        import threading
        
        def server_thread():
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind(('0.0.0.0', port))
                self.socket.listen(1)
                
                # 等待连接
                self.client_socket, self.client_address = self.socket.accept()
                self.is_connected = True
                self.is_server = True
                
                # 开始接收数据
                self.receive_thread = threading.Thread(target=self.receive_data)
                self.receive_thread.daemon = True
                self.receive_thread.start()
                
                QMessageBox.information(self, "提示", f"已连接到客户端: {self.client_address}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"启动服务器失败: {str(e)}")
        
        self.server_thread = threading.Thread(target=server_thread)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def connect_to_server(self, host, port=5555):
        """连接到服务器"""
        import socket
        import threading
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.is_connected = True
            self.is_server = False
            
            # 开始接收数据
            self.receive_thread = threading.Thread(target=self.receive_data)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            QMessageBox.information(self, "提示", f"已连接到服务器: {host}:{port}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"连接服务器失败: {str(e)}")
    
    def receive_data(self):
        """接收数据"""
        while self.is_connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if data:
                    self.process_network_data(data)
            except Exception:
                self.is_connected = False
                break
    
    def process_network_data(self, data):
        """处理网络数据"""
        # 数据格式：from_row,from_col,to_row,to_col
        from_row, from_col, to_row, to_col = map(int, data.split(','))
        
        # 执行移动
        self.move_piece(from_row, from_col, to_row, to_col)
        
        # 检查游戏是否结束
        if self.is_game_over():
            # 开始庆祝特效
            self.start_celebration()
            winner = self.get_winner()
            # 使用回调函数显示游戏结束信息
            if self.game_over_callback:
                self.game_over_callback(winner)
            else:
                QMessageBox.information(self, "游戏结束", f"{winner}获胜！")
            return
        
        # 切换玩家
        self.switch_player()
        
        # 重绘棋盘
        self.update()
    
    def send_move(self, from_row, from_col, to_row, to_col):
        """发送移动数据"""
        if self.is_connected:
            data = f"{from_row},{from_col},{to_row},{to_col}"
            self.socket.sendall(data.encode('utf-8'))
    
    def is_game_over(self):
        """检查游戏是否结束"""
        # 检查是否有一方的将/帅被吃掉
        red_jiang = False
        black_jiang = False
        
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece:
                    if (piece["name"] == "将" or piece["name"] == "帅") and piece["color"] == "red":
                        red_jiang = True
                    elif (piece["name"] == "将" or piece["name"] == "帅") and piece["color"] == "black":
                        black_jiang = True
        
        return not red_jiang or not black_jiang
    
    def get_winner(self):
        """获取获胜者"""
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece and (piece["name"] == "将" or piece["name"] == "帅"):
                    return "红方" if piece["color"] == "red" else "黑方"
        return ""
