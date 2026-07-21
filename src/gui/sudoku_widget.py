from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QPainter, QPen, QFont, QColor

class SudokuWidget(QWidget):
    error_made = Signal(int)
    game_over = Signal(bool)
    hints_used = Signal(int)
    board_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(450, 450)
        self.setMaximumSize(600, 600)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.fixed = [[False for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.cell_size = 0
        self.solution = None
        self.lives = 3
        self.errors = []
        self.is_game_mode = False
        self.is_game_over = False
        self.history = []
        self.hints_remaining = 3
        
    def reset_board(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.fixed = [[False for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.solution = None
        self.lives = 3
        self.errors = []
        self.is_game_mode = False
        self.is_game_over = False
        self.history = []
        self.hints_remaining = 3
        self.update()
        
    def set_board(self, board, solution=None, is_game_mode=False):
        self.board = [row[:] for row in board]
        self.solution = solution
        self.is_game_mode = is_game_mode
        self.errors = []
        self.is_game_over = False
        self.history = []
        self.hints_remaining = 3
        if is_game_mode:
            self.lives = 3
        self.update()
        
    def get_board(self):
        return [row[:] for row in self.board]
        
    def save_state(self):
        self.history.append({
            'board': [row[:] for row in self.board],
            'errors': self.errors[:]
        })
        
    def undo(self):
        if self.history:
            state = self.history.pop()
            self.board = state['board']
            self.errors = state['errors']
            self.update()
            self.board_changed.emit()
            
    def use_hint(self):
        if self.hints_remaining > 0 and self.selected_cell and self.solution:
            row, col = self.selected_cell
            if not self.fixed[row][col] and self.board[row][col] != self.solution[row][col]:
                self.save_state()
                self.board[row][col] = self.solution[row][col]
                if (row, col) in self.errors:
                    self.errors.remove((row, col))
                self.hints_remaining -= 1
                self.hints_used.emit(self.hints_remaining)
                self.update()
                self.board_changed.emit()
                return True
        return False
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        available_width = self.width()
        available_height = self.height()
        size = min(available_width, available_height)
        self.cell_size = size // 9
        offset_x = (available_width - size) // 2
        offset_y = (available_height - size) // 2
        painter.fillRect(0, 0, available_width, available_height, QColor(255, 255, 255))
        self.grid_offset_x = offset_x
        self.grid_offset_y = offset_y
        
        self._draw_highlights(painter, size, offset_x, offset_y)
        self._draw_grid(painter, size, offset_x, offset_y)
        self._draw_numbers(painter, size, offset_x, offset_y)
        
    def _draw_grid(self, painter, size, offset_x, offset_y):
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        thin_pen = QPen(QColor(210, 210, 210), 1)
        painter.setPen(thin_pen)
        for i in range(10):
            x = int(offset_x + i * self.cell_size)
            y = int(offset_y + i * self.cell_size)
            painter.drawLine(x, int(offset_y), x, int(offset_y + size))
            painter.drawLine(int(offset_x), y, int(offset_x + size), y)
        
        thick_pen = QPen(QColor(50, 50, 50), 3)
        painter.setPen(thick_pen)
        for i in range(0, 10, 3):
            x = int(offset_x + i * self.cell_size)
            y = int(offset_y + i * self.cell_size)
            painter.drawLine(x, int(offset_y), x, int(offset_y + size))
            painter.drawLine(int(offset_x), y, int(offset_x + size), y)
            
        painter.setRenderHint(QPainter.Antialiasing, True)
            
    def _draw_highlights(self, painter, size, offset_x, offset_y):
        if not self.selected_cell or self.is_game_over:
            return
        sel_row, sel_col = self.selected_cell
        selected_num = self.board[sel_row][sel_col]
        
        block_row = (sel_row // 3) * 3
        block_col = (sel_col // 3) * 3
        
        block_highlight = QColor(232, 240, 248, 180)
        painter.fillRect(
            int(offset_x + block_col * self.cell_size), 
            int(offset_y + block_row * self.cell_size),
            int(3 * self.cell_size), int(3 * self.cell_size),
            block_highlight
        )
        
        row_col_highlight = QColor(232, 240, 248, 150)
        
        for col in range(9):
            if not (block_col <= col < block_col + 3):
                painter.fillRect(
                    int(offset_x + col * self.cell_size), 
                    int(offset_y + sel_row * self.cell_size), 
                    int(self.cell_size), int(self.cell_size), 
                    row_col_highlight
                )
        
        for row in range(9):
            if not (block_row <= row < block_row + 3):
                painter.fillRect(
                    int(offset_x + sel_col * self.cell_size), 
                    int(offset_y + row * self.cell_size), 
                    int(self.cell_size), int(self.cell_size), 
                    row_col_highlight
                )

        if selected_num != 0:
            highlight_num_color = QColor(200, 220, 245, 150)
            for r in range(9):
                for c in range(9):
                    if self.board[r][c] == selected_num and (r, c) != (sel_row, sel_col):
                        x = int(offset_x + c * self.cell_size)
                        y = int(offset_y + r * self.cell_size)
                        painter.fillRect(x, y, int(self.cell_size), int(self.cell_size), highlight_num_color)

        x = int(offset_x + sel_col * self.cell_size)
        y = int(offset_y + sel_row * self.cell_size)
        painter.fillRect(x, y, int(self.cell_size), int(self.cell_size), QColor(173, 216, 230, 200))

        if (sel_row, sel_col) in self.errors and selected_num != 0:
            conflict_color = QColor(255, 200, 200, 200)
            for c in range(9):
                if c != sel_col and self.board[sel_row][c] == selected_num:
                    x = int(offset_x + c * self.cell_size)
                    y = int(offset_y + sel_row * self.cell_size)
                    painter.fillRect(x, y, int(self.cell_size), int(self.cell_size), conflict_color)
            for r in range(9):
                if r != sel_row and self.board[r][sel_col] == selected_num:
                    x = int(offset_x + sel_col * self.cell_size)
                    y = int(offset_y + r * self.cell_size)
                    painter.fillRect(x, y, int(self.cell_size), int(self.cell_size), conflict_color)
            for r in range(block_row, block_row + 3):
                for c in range(block_col, block_col + 3):
                    if (r, c) != (sel_row, sel_col) and self.board[r][c] == selected_num:
                        x = int(offset_x + c * self.cell_size)
                        y = int(offset_y + r * self.cell_size)
                        painter.fillRect(x, y, int(self.cell_size), int(self.cell_size), conflict_color)
                        
    def _draw_numbers(self, painter, size, offset_x, offset_y):
        font = QFont("Arial", 22, QFont.Normal)
        painter.setFont(font)
        for row in range(9):
            for col in range(9):
                num = self.board[row][col]
                if num != 0:
                    is_error = (row, col) in self.errors
                    if is_error:
                        painter.setPen(QColor(255, 0, 0))
                    elif self.fixed[row][col]:
                        painter.setPen(QColor(30, 30, 30))
                    else:
                        painter.setPen(QColor(41, 121, 255))
                    text_rect = QRect(
                        int(offset_x + col * self.cell_size), 
                        int(offset_y + row * self.cell_size), 
                        int(self.cell_size), 
                        int(self.cell_size)
                    )
                    painter.drawText(text_rect, Qt.AlignCenter, str(num))
                    
    def get_remaining_numbers(self):
        counts = {i: 0 for i in range(1, 10)}
        for row in range(9):
            for col in range(9):
                num = self.board[row][col]
                if num != 0:
                    counts[num] += 1
        remaining = []
        for num in range(1, 10):
            if counts[num] < 9:
                remaining.append(num)
        return remaining
    
    def get_numbers_count(self):
        counts = {i: 0 for i in range(1, 10)}
        for row in range(9):
            for col in range(9):
                num = self.board[row][col]
                if num != 0:
                    counts[num] += 1
        return counts
        
    def mousePressEvent(self, event):
        if self.is_game_over:
            return
        if event.button() == Qt.LeftButton:
            if hasattr(self, 'grid_offset_x'):
                col = (event.x() - self.grid_offset_x) // self.cell_size
                row = (event.y() - self.grid_offset_y) // self.cell_size
            else:
                col = event.x() // self.cell_size
                row = event.y() // self.cell_size
            if 0 <= row < 9 and 0 <= col < 9:
                self.selected_cell = (row, col)
                self.setFocus()
                self.update()
                
    def keyPressEvent(self, event):
        if self.is_game_over:
            return
        if self.selected_cell:
            row, col = self.selected_cell
            if not self.fixed[row][col]:
                key = event.key()
                if Qt.Key_1 <= key <= Qt.Key_9:
                    num = key - Qt.Key_0
                    self._try_set_number(row, col, num)
                elif key in (Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_0):
                    self.save_state()
                    self.board[row][col] = 0
                    if (row, col) in self.errors:
                        self.errors.remove((row, col))
                    self.update()
                    self.board_changed.emit()
        
        key = event.key()
        if key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right):
            self._move_selection(key)
                    
    def _move_selection(self, key):
        if not self.selected_cell:
            self.selected_cell = (0, 0)
            self.update()
            return
            
        row, col = self.selected_cell
        if key == Qt.Key_Up:
            row = max(0, row - 1)
        elif key == Qt.Key_Down:
            row = min(8, row + 1)
        elif key == Qt.Key_Left:
            col = max(0, col - 1)
        elif key == Qt.Key_Right:
            col = min(8, col + 1)
            
        self.selected_cell = (row, col)
        self.update()
                    
    def _try_set_number(self, row, col, num):
        if self.solution and self.board[row][col] == self.solution[row][col]:
            return
        self.save_state()
        self.board[row][col] = num
        if self.is_game_mode and self.solution:
            correct_num = self.solution[row][col]
            if num != correct_num:
                if (row, col) not in self.errors:
                    self.errors.append((row, col))
                    self.lives -= 1
                    self.error_made.emit(self.lives)
                    if self.lives <= 0:
                        self.is_game_over = True
                        self.game_over.emit(False)
            else:
                if (row, col) in self.errors:
                    self.errors.remove((row, col))
        self.update()
        self.board_changed.emit()
        if self.is_game_mode and self.solution:
            self._check_win_condition()
            
    def _check_win_condition(self):
        if self.is_game_over:
            return
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    return
        if len(self.errors) > 0:
            return
        for row in range(9):
            for col in range(9):
                if self.board[row][col] != self.solution[row][col]:
                    return
        self.is_game_over = True
        self.game_over.emit(True)
