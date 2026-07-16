from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QLabel, QMenuBar, QMessageBox, QPushButton,
    QHBoxLayout, QComboBox
)
from PySide6.QtCore import Qt
from src.gui.sudoku_widget import SudokuWidget
from src.logic.solver import solve, is_valid_board
from src.logic.generator import generate_sudoku

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

        top_panel = QHBoxLayout()
        difficulty_label = QLabel("Выберите сложность:")
        difficulty_label.setStyleSheet("font-size: 16px;")
        top_panel.addWidget(difficulty_label)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Легкий", "Средний", "Сложный"])
        self.difficulty_combo.setStyleSheet("font-size: 16px; padding: 5px;")
        top_panel.addWidget(self.difficulty_combo)

        top_panel.addStretch()
        layout.addLayout(top_panel)
        
        self.game_grid = SudokuWidget()
        layout.addWidget(self.game_grid)
        
        bottom_panel = QHBoxLayout()
        
        new_game_button = QPushButton("🎲 Новая игра")
        new_game_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        new_game_button.clicked.connect(self._new_game)
        bottom_panel.addWidget(new_game_button)
        
        check_button = QPushButton("✓ Проверить")
        check_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        check_button.clicked.connect(self._check_solution)
        bottom_panel.addWidget(check_button)
        
        layout.addLayout(bottom_panel)
        
        self.tabs.addTab(game_widget, "🎮 Игра")

    def _new_game(self):
        self.game_grid.reset_board()
        difficulty_index = self.difficulty_combo.currentIndex()
        difficulty_map = {0: 'easy', 1: 'medium', 2: 'hard'}
        difficulty = difficulty_map[difficulty_index]
        
        puzzle, solution = generate_sudoku(difficulty)
        
        self.current_solution = solution
        
        self.game_grid.set_board(puzzle)
        
        for row in range(9):
            for col in range(9):
                if puzzle[row][col] != 0:
                    self.game_grid.fixed[row][col] = True
        
        self.game_grid.update()
        
        QMessageBox.information(
            self, 
            "Новая игра", 
            f"Сгенерирована новая игра!\nУровень сложности: {self.difficulty_combo.currentText()}\n\nУдачи!"
        )

    def _check_solution(self):
        if self.current_solution is None:
            QMessageBox.warning(self, "Ошибка", "Сначала начните новую игру!")
            return
        
        current_board = self.game_grid.get_board()
        
        for row in range(9):
            for col in range(9):
                if current_board[row][col] == 0:
                    QMessageBox.warning(
                        self, 
                        "Не завершено", 
                        "Заполните все клетки перед проверкой!"
                    )
                    return
        
        if current_board == self.current_solution:
            QMessageBox.information(
                self, 
                "Поздравляем!", 
                "🎉 Вы решили судоку правильно!\n\nОтличная работа!"
            )
        else:
            QMessageBox.warning(
                self, 
                "Неверно", 
                "Решение неверное.\n\nПроверьте свои ответы и попробуйте еще раз!"
            )

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
