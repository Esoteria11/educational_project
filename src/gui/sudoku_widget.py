from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen, QFont, QColor

class SudokuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)

        self.setMinimumSize(450, 450)
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.fixed = [[False for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.cell_size = 0

    def reset_board(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.fixed = [[False for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.update()

    def set_board(self, board):
        self.board = [row[:] for row in board]
        self.update()

    def get_board(self):
        return [row[:] for row in self.board]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        size = min(self.width(), self.height())
        self.cell_size = size // 9

        painter.fillRect(0, 0, size, size, QColor(255, 255, 255))
        self._draw_grid(painter, size)
        self._draw_numbers(painter)
        if self.selected_cell:
            self._draw_selection(painter)

    def _draw_grid(self, painter, size):
        thin_pen = QPen(QColor(150, 150, 150), 1)
        painter.setPen(thin_pen)
        
        for i in range(10):
            x = i * self.cell_size
            painter.drawLine(x, 0, x, size)
            y = i * self.cell_size
            painter.drawLine(0, y, size, y)
        
        thick_pen = QPen(QColor(0, 0, 0), 3)
        painter.setPen(thick_pen)
        
        for i in range(0, 10, 3):
            x = i * self.cell_size
            painter.drawLine(x, 0, x, size)
            y = i * self.cell_size
            painter.drawLine(0, y, size, y)

    def _draw_numbers(self, painter):
        font = QFont("Arial", 18, QFont.Bold)
        painter.setFont(font)
        
        for row in range(9):
            for col in range(9):
                num = self.board[row][col]
                if num != 0:
                    x = col * self.cell_size + self.cell_size // 2
                    y = row * self.cell_size + self.cell_size // 2
                    
                    if self.fixed[row][col]:
                        painter.setPen(QColor(0, 0, 0))
                    else:
                        painter.setPen(QColor(0, 0, 200))
                    
                    text_rect = QRect(
                        col * self.cell_size, 
                        row * self.cell_size, 
                        self.cell_size, 
                        self.cell_size
                    )
                    painter.drawText(text_rect, Qt.AlignCenter, str(num))

    def _draw_selection(self, painter):
        if self.selected_cell:
            row, col = self.selected_cell
            x = col * self.cell_size
            y = row * self.cell_size
            
            painter.fillRect(x, y, self.cell_size, self.cell_size, QColor(100, 150, 255, 100))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            col = event.x() // self.cell_size
            row = event.y() // self.cell_size
            
            if 0 <= row < 9 and 0 <= col < 9:
                self.selected_cell = (row, col)
                self.setFocus()
                self.update()

    def keyPressEvent(self, event):
        if self.selected_cell:
            row, col = self.selected_cell
            
            if not self.fixed[row][col]:
                key = event.key()
                
                if Qt.Key_1 <= key <= Qt.Key_9:
                    num = key - Qt.Key_0
                    self.board[row][col] = num
                    self.update()
                
                elif key in (Qt.Key_Backspace, Qt.Key_Delete):
                    self.board[row][col] = 0
                    self.update()
