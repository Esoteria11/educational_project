from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QPainter, QPen, QFont, QColor

class SudokuWidget(QWidget):
    error_made = Signal(int)
    game_over = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(400, 400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.fixed = [[False for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.cell_size = 0
        self.solution = None
        self.lives = 3
        self.errors = []
        self.is_game_mode = False
        self.is_game_over = False

    def reset_board(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.fixed = [[False for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.solution = None
        self.lives = 3
        self.errors = []
        self.is_game_mode = False
        self.is_game_over = False
        self.update()

    def set_board(self, board, solution=None, is_game_mode=False):
        self.board = [row[:] for row in board]
        self.solution = solution
        self.is_game_mode = is_game_mode
        self.errors = []
        self.is_game_over = False
        if is_game_mode:
            self.lives = 3
        self.update()

    def get_board(self):
        return [row[:] for row in self.board]

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
        self._draw_grid(painter, size, offset_x, offset_y)
        self._draw_highlights(painter, size, offset_x, offset_y)
        self._draw_numbers(painter, size, offset_x, offset_y)

    def _draw_grid(self, painter, size, offset_x, offset_y):
        thin_pen = QPen(QColor(200, 200, 200), 1)
        painter.setPen(thin_pen)
        for i in range(10):
            x = offset_x + i * self.cell_size
            y = offset_y + i * self.cell_size
            painter.drawLine(x, offset_y, x, offset_y + size)
            painter.drawLine(offset_x, y, offset_x + size, y)
        thick_pen = QPen(QColor(0, 0, 0), 3)
        painter.setPen(thick_pen)
        for i in range(0, 10, 3):
            x = offset_x + i * self.cell_size
            y = offset_y + i * self.cell_size
            painter.drawLine(x, offset_y, x, offset_y + size)
            painter.drawLine(offset_x, y, offset_x + size, y)

    def _draw_highlights(self, painter, size, offset_x, offset_y):
        if not self.selected_cell or self.is_game_over:
            return
        sel_row, sel_col = self.selected_cell
        selected_num = self.board[sel_row][sel_col]
        highlight_area_color = QColor(220, 220, 220, 150)
        painter.fillRect(
            offset_x, offset_y + sel_row * self.cell_size, 
            size, self.cell_size, 
            highlight_area_color
        )
        painter.fillRect(
            offset_x + sel_col * self.cell_size, offset_y, 
            self.cell_size, size, 
            highlight_area_color
        )
        block_row = (sel_row // 3) * 3
        block_col = (sel_col // 3) * 3
        painter.fillRect(
            offset_x + block_col * self.cell_size, 
            offset_y + block_row * self.cell_size,
            3 * self.cell_size, 3 * self.cell_size,
            highlight_area_color
        )
        if selected_num != 0:
            highlight_num_color = QColor(173, 216, 230, 180)
            for r in range(9):
                for c in range(9):
                    if self.board[r][c] == selected_num:
                        x = offset_x + c * self.cell_size
                        y = offset_y + r * self.cell_size
                        painter.fillRect(x, y, self.cell_size, self.cell_size, highlight_num_color)
        x = offset_x + sel_col * self.cell_size
        y = offset_y + sel_row * self.cell_size
        painter.fillRect(x, y, self.cell_size, self.cell_size, QColor(135, 206, 250, 200))
        error_color = QColor(255, 100, 100, 150)
        for err_row, err_col in self.errors:
            x = offset_x + err_col * self.cell_size
            y = offset_y + err_row * self.cell_size
            painter.fillRect(x, y, self.cell_size, self.cell_size, error_color)

    def _draw_numbers(self, painter, size, offset_x, offset_y):
        font = QFont("Arial", 20, QFont.Bold)
        painter.setFont(font)
        for row in range(9):
            for col in range(9):
                num = self.board[row][col]
                if num != 0:
                    is_error = (row, col) in self.errors
                    if is_error:
                        painter.setPen(QColor(255, 0, 0))
                    elif self.fixed[row][col]:
                        painter.setPen(QColor(0, 0, 0))
                    else:
                        painter.setPen(QColor(33, 150, 243))
                    text_rect = QRect(
                        offset_x + col * self.cell_size, 
                        offset_y + row * self.cell_size, 
                        self.cell_size, 
                        self.cell_size
                    )
                    painter.drawText(text_rect, Qt.AlignCenter, str(num))

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
                    self.board[row][col] = 0
                    if (row, col) in self.errors:
                        self.errors.remove((row, col))
                    self.update()

    def _try_set_number(self, row, col, num):
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
