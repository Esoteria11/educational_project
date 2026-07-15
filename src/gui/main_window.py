from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QLabel, QMenuBar, QMessageBox, QPushButton
)
from PySide6.QtCore import Qt
from src.gui.sudoku_widget import SudokuWidget
from src.logic.solver import solve, is_valid_board

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Судоку")
        self.resize(600, 650)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._create_game_tab()
        self._create_solver_tab()
        self._create_menu()

    def _create_game_tab(self):
        game_widget = QWidget()
        layout = QVBoxLayout(game_widget)

        label = QLabel("Поле для игры\n(Генератор + Игрок)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; color: gray;")
        layout.addWidget(label)

        self.tabs.addTab(game_widget, "Игра")

    def _create_solver_tab(self):
        solver_widget = QWidget()
        layout = QVBoxLayout(solver_widget)
        
        self.sudoku_grid = SudokuWidget()
        layout.addWidget(self.sudoku_grid)
        
        solve_button = QPushButton("Решить")
        solve_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        solve_button.clicked.connect(self._solve_sudoku)
        layout.addWidget(solve_button)
        
        clear_button = QPushButton("Очистить")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        clear_button.clicked.connect(self._clear_board)
        layout.addWidget(clear_button)
        
        self.tabs.addTab(solver_widget, "Решатель")

    def _solve_sudoku(self):
        board = self.sudoku_grid.get_board()

        if not is_valid_board(board):
            QMessageBox.critical(
                self,
                "Ошибка ввода",
                "Исходные данные нарушают правила судоку\n\n"
                "Проверьте, нет ли повторяющихся цифр в строках, столбцах или квадратах 3х3"
            )
            return
        
        if solve(board):
            self.sudoku_grid.set_board(board)
            QMessageBox.information(self, "Успех", "Судоку решено!")
        else:
            QMessageBox.warning(self, "Ошибка", "Решение не найдено. Проверьте исходные данные.")

    def _clear_board(self):
        empty_board = [[0 for _ in range(9)] for _ in range(9)]
        self.sudoku_grid.set_board(empty_board)

    def _create_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("Файл")
        
        exit_action = file_menu.addAction("Выход")
        exit_action.triggered.connect(self.close) 
        
        help_menu = menu_bar.addMenu("Справка")
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self.show_about_dialog)

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "О программе",
            "<h3>Судоку: игра и решатель</h3>"
            "<p><b>Цель игры:</b> Заполнить сетку 9x9 так, чтобы в каждой строке, "
            "каждом столбце и каждом малом квадрате 3x3 встречались все цифры от 1 до 9.</p>"
            "<p><b>Управление:</b> Используйте мышь и клавиатуру для ввода цифр.</p>"
        )
