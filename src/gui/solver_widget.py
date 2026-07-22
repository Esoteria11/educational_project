from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QPainter, QPen, QFont, QColor

class SolverWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(450, 450)
        self.setMaximumSize(600, 600)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.initial_board = [[0 for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.cell_size = 0
        
    def clear_board(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.initial_board = [[0 for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.update()
        
    def get_board(self):
        return [row[:] for row in self.board]
        
    def set_cell(self, row, col, num):
        self.board[row][col] = num
        if self.initial_board[row][col] == 0 and num != 0:
            pass
        self.selected_cell = (row, col)
        self.update()
        
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
        if not self.selected_cell:
            return
        sel_row, sel_col = self.selected_cell
        x = int(offset_x + sel_col * self.cell_size)
        y = int(offset_y + sel_row * self.cell_size)
        painter.fillRect(x, y, int(self.cell_size), int(self.cell_size), QColor(173, 216, 230, 200))

    def _has_conflict(self, row, col, num):
        if num == 0:
            return False
        for i in range(9):
            if i != col and self.board[row][i] == num: return True
            if i != row and self.board[i][col] == num: return True
        box_r, box_c = (row // 3) * 3, (col // 3) * 3
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if (r, c) != (row, col) and self.board[r][c] == num:
                    return True
        return False

    def _draw_numbers(self, painter, size, offset_x, offset_y):
        font = QFont("Arial", 22, QFont.Normal)
        painter.setFont(font)
        for row in range(9):
            for col in range(9):
                num = self.board[row][col]
                if num != 0:
                    if self._has_conflict(row, col, num):
                        painter.setPen(QColor(255, 0, 0))
                    elif self.initial_board[row][col] != 0:
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
                    
    def mousePressEvent(self, event):
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
        if self.selected_cell:
            row, col = self.selected_cell
            key = event.key()
            if Qt.Key_1 <= key <= Qt.Key_9:
                num = key - Qt.Key_0
                self.board[row][col] = num
                if self.initial_board[row][col] == 0:
                    pass
                self.update()
            elif key in (Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_0):
                self.board[row][col] = 0
                self.update()
        
        key = event.key()
        if key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right):
            self._move_selection(key)
                    
    def _move_selection(self, key):
        if not self.selected_cell:
            self.selected_cell = (0, 0)
            self.update()
            return
        row, col = self.selected_cell
        if key == Qt.Key_Up: row = max(0, row - 1)
        elif key == Qt.Key_Down: row = min(8, row + 1)
        elif key == Qt.Key_Left: col = max(0, col - 1)
        elif key == Qt.Key_Right: col = min(8, col + 1)
        self.selected_cell = (row, col)
        self.update()
