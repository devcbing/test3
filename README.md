# 中国象棋游戏

一个基于PyQt5开发的中国象棋游戏，支持人机对战和联机对战，并包含精美的特效效果。

## 项目结构

```
test3/
├── __pycache__/          # Python编译缓存文件
├── chess_board.py        # 棋盘和游戏逻辑实现
├── main.py               # 主程序入口和界面
├── network_dialog.py     # 网络对战对话框
└── README.md             # 项目文档
```

## 功能说明

### 核心功能
- **中国象棋规则**：完整实现中国象棋的标准规则
- **人机对战**：简单的AI对手
- **联机对战**：支持网络对战功能
- **悔棋功能**：可以撤销上一步操作
- **认输功能**：玩家可以选择认输结束游戏

### 特效效果
- **吃棋爆炸特效**：吃掉对方棋子时显示爆炸效果
- **获胜庆祝特效**：游戏结束时显示"完结撒花"效果
- **将军提示特效**：出现将军情况时，在棋盘中间以爆炸方式弹出提示文字
- **精美获胜弹窗**：自定义的游戏结束弹窗，带有动画效果

## 安装和运行

### 环境要求
- Python 3.x
- PyQt5

### 安装依赖
```bash
pip install pyqt5
```

### 运行游戏
```bash
python main.py
```

## 游戏操作

### 基本操作
1. **选择棋子**：点击要移动的棋子
2. **移动棋子**：点击目标位置移动棋子
3. **悔棋**：点击菜单栏中的"悔棋"选项
4. **认输**：点击菜单栏中的"认输"选项

### 游戏模式
1. **人机对战**：选择"人机对战"菜单项
2. **联机对战**：选择"联机对战"菜单项，设置服务器或客户端

## 技术实现

### 界面设计
使用PyQt5框架构建图形界面，采用QMainWindow作为主窗口，QWidget作为棋盘容器。

### 游戏逻辑
- **棋盘表示**：使用二维数组表示棋盘状态
- **棋子移动**：实现了所有棋子的移动规则
- **游戏状态检查**：判断游戏是否结束，确定获胜者

### 特效实现
1. **爆炸特效**
   - 使用QTimer实现动画效果
   - 粒子系统模拟爆炸效果
   - 根据棋子颜色显示不同颜色的爆炸

2. **庆祝特效**
   - 随机生成彩色粒子
   - 粒子带有重力和旋转效果
   - 渐隐动画效果

3. **将军提示特效**
   - 棋盘中间爆炸弹出提示
   - 快速消失不影响继续走棋
   - 动态脉冲和大小变化效果

4. **自定义弹窗**
   - 圆角设计和金色边框
   - 动画效果
   - 友好的交互体验

### 网络功能
- 使用socket实现网络通信
- 支持服务器和客户端模式
- 实时同步游戏状态

## 扩展功能

### 未来可以扩展的功能
- 更高级的AI算法
- 游戏记录保存和回放
- 更多的特效效果
- 音效支持
- 多语言支持

## 代码结构

### 核心类和功能

#### ChessBoard 类 (chess_board.py)

**主要功能**：实现棋盘绘制、棋子移动规则和游戏状态管理。

**关键方法**：
- `__init__()`: 初始化棋盘和游戏状态，设置特效定时器
- `init_board()`: 初始化棋盘尺寸和棋子位置
- `init_pieces()`: 布置初始棋子
- `paintEvent()`: 绘制棋盘、棋子和特效
- `mousePressEvent()`: 处理鼠标点击事件，实现棋子选择和移动
- `can_move()`: 检查棋子是否可以移动到目标位置
- `move_piece()`: 移动棋子并处理吃子逻辑
- `check_game_over()`: 检查游戏是否结束
- `is_checked()`: 检查是否有玩家被将军

**特效相关方法**：
- `create_explosion()`: 创建爆炸特效
- `update_explosions()`: 更新爆炸特效状态
- `draw_explosions()`: 绘制爆炸特效
- `start_celebration()`: 开始庆祝特效
- `update_celebration()`: 更新庆祝特效状态
- `draw_celebration()`: 绘制庆祝特效
- `show_check_effect()`: 显示将军提示特效
- `update_check_effects()`: 更新将军特效状态
- `draw_check_effects()`: 绘制将军特效

#### VictoryDialog 类 (main.py)

**主要功能**：自定义获胜弹窗，提供精美的视觉效果。

**实现细节**：
- 使用半透明背景和金色边框
- 包含奖杯图标和动画效果
- 响应式布局设计
- 自定义样式表美化界面

#### ChineseChessGame 类 (main.py)

**主要功能**：主窗口和游戏控制。

**关键方法**：
- `__init__()`: 初始化主窗口和菜单
- `create_menu()`: 创建游戏菜单
- `start_game()`: 开始新游戏
- `start_ai_game()`: 开始人机对战
- `start_network_game()`: 开始网络对战
- `undo_move()`: 悔棋功能
- `resign()`: 认输功能

### network_dialog.py

**主要功能**：网络对战设置对话框。

**实现细节**：
- 支持服务器和客户端模式
- IP地址和端口设置
- 网络连接状态显示

## 特效实现技术

### 爆炸特效

**实现原理**：
- 使用粒子系统模拟爆炸效果
- 每个爆炸包含多个粒子，从中心点向外扩散
- 粒子具有随机速度、大小和颜色
- 使用QTimer控制动画更新频率
- 粒子逐渐消失，当所有粒子消失时爆炸结束

**核心代码**：
```python
# 创建爆炸
self.create_explosion(to_row, to_col, piece_color)

# 更新爆炸状态
self.update_explosions()

# 绘制爆炸
self.draw_explosions(painter)
```

### 庆祝特效

**实现原理**：
- 随机生成彩色粒子（彩花）
- 粒子具有随机大小、速度和角度
- 添加重力效果，使粒子向下飘落
- 粒子旋转并逐渐消失
- 使用QTimer每30毫秒更新一次粒子状态

**核心代码**：
```python
# 开始庆祝
self.start_celebration()

# 更新庆祝特效
self.update_celebration()

# 绘制庆祝特效
self.draw_celebration(painter)
```

### 将军提示特效

**实现原理**：
- 在棋盘中间位置创建爆炸弹出效果
- 提示文字随爆炸动态变化大小
- 快速消失不影响继续走棋
- 使用QTimer实现50ms间隔的动画更新

**核心代码**：
```python
# 检查是否被将军
if self.is_checked(enemy_color):
    self.show_check_effect(enemy_color)

# 更新将军特效
self.update_check_effects()

# 绘制将军特效
self.draw_check_effects(painter)
```

**特效特点**：
- 爆炸半径限制在棋盘范围内
- 文字居中显示在棋盘中央
- 透明度快速降低实现快速消失
- 脉冲动画增强视觉冲击力

### 自定义弹窗

**实现原理**：
- 使用QDialog创建自定义对话框
- 采用无边框窗口和半透明背景
- 应用CSS样式美化界面
- 添加动画效果增强视觉体验

**核心代码**：
```python
# 创建自定义弹窗
class VictoryDialog(QDialog):
    def __init__(self, winner, parent=None):
        super().__init__(parent)
        self.setWindowTitle("游戏结束")
        self.setFixedSize(400, 250)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置样式和布局
        # ...
```

## 开发说明

### 如何添加新的特效

1. **创建特效类或方法**：在chess_board.py中实现特效的创建、更新和绘制方法
2. **设置动画控制**：使用QTimer控制特效的更新频率（建议30ms）
3. **触发条件设置**：在适当的游戏事件中触发特效（如吃棋、获胜等）
4. **绘制实现**：在paintEvent方法中调用特效的绘制方法
5. **资源管理**：确保特效结束后释放资源，避免内存泄漏

**示例**：
```python
# 创建特效方法
def create_new_effect(self, x, y):
    # 特效初始化逻辑
    pass

# 更新特效状态
def update_new_effect(self):
    # 特效动画逻辑
    pass

# 绘制特效
def draw_new_effect(self, painter):
    # 特效绘制逻辑
    pass

# 触发特效
# 在适当的位置调用
self.create_new_effect(row, col)
```

### 如何修改游戏规则

1. **修改移动规则**：更新chess_board.py中的can_move方法和相应的棋子移动规则方法
2. **测试验证**：确保修改后的规则符合预期
3. **更新文档**：如果修改了核心规则，记得更新相关文档

**示例**：
```python
def can_move_jiang(self, from_row, from_col, to_row, to_col):
    # 修改将/帅的移动规则
    # ...
    return True/False
```

### 代码优化建议

1. **AI算法优化**：当前AI较为简单，可以实现更高级的算法（如极小极大算法）
2. **性能优化**：在特效实现中添加对象池，避免频繁创建和销毁对象
3. **代码结构**：将特效逻辑封装为独立的类，提高代码可维护性
4. **国际化**：添加多语言支持

## 使用示例

### 基本游戏流程

1. **启动游戏**：运行`python main.py`
2. **选择游戏模式**：
   - 点击"新游戏"开始玩家对战
   - 点击"人机对战"开始与AI对战
   - 点击"联机对战"开始网络对战
3. **移动棋子**：
   - 点击要移动的棋子（选中的棋子会有高亮效果）
   - 点击目标位置移动棋子
4. **游戏结束**：
   - 当一方将/帅被将死时，游戏结束
   - 会显示精美的获胜弹窗和庆祝特效
   - 可以选择"新游戏"重新开始

### 人机对战示例

1. **选择"人机对战"**：在菜单中点击"人机对战"选项
2. **玩家先行**：红方先行，点击棋子进行移动
3. **AI响应**：AI会自动进行下一步移动
4. **游戏结束**：与标准游戏相同

## 扩展功能建议

### 近期可实现的功能

1. **音效系统**：添加棋子移动、吃子、获胜等音效
2. **游戏记录**：保存和加载游戏记录
3. **难度选择**：为AI添加不同难度等级
4. **皮肤系统**：支持自定义棋盘和棋子皮肤

### 远期扩展功能

1. **多人在线对战平台**：实现服务器端，支持多人在线对战
2. **残局库**：添加经典残局供玩家练习
3. **教学模式**：提供象棋教程和规则讲解
4. **移动版本**：开发移动设备版本

## 许可证

本项目采用MIT许可证，可自由使用和修改。

```
MIT License

Copyright (c) 2024 中国象棋游戏项目

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```