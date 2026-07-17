from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QLabel, QMenuBar, QMessageBox, QPushButton,
    QHBoxLayout, QComboBox, QDialog, QDialogButtonBox,
    QListWidget, QListWidgetItem, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTime, QTimer
from src.gui.sudoku_widget import SudokuWidget
from src.logic.solver import solve, is_valid_board
from src.logic.generator import generate_sudoku
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Судоку")
        self.resize(800, 700)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.game_timer = None
        self.game_start_time = None
        self.saved_difficulty = 1
        self._create_game_tab()
        self._create_solver_tab()
        self._create_menu()
        self.difficulty_combo.setCurrentIndex(self.saved_difficulty)

    def _create_game_tab(self):
        game_widget = QWidget()
        layout = QVBoxLayout(game_widget)
        top_panel = QHBoxLayout()
        difficulty_label = QLabel("Сложность:")
        difficulty_label.setStyleSheet("font-size: 14px;")
        top_panel.addWidget(difficulty_label)
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Легкий", "Средний", "Сложный"])
        self.difficulty_combo.setStyleSheet("font-size: 14px; padding: 5px;")
        top_panel.addWidget(self.difficulty_combo)
        top_panel.addStretch()
        self.lives_label = QLabel("❤️❤️❤️")
        self.lives_label.setStyleSheet("font-size: 18px; color: red;")
        top_panel.addWidget(self.lives_label)
        layout.addLayout(top_panel)
        self.timer_label = QLabel("Время: 00:00")
        self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timer_label)
        self.game_grid = SudokuWidget()
        self.game_grid.error_made.connect(self._on_error_made)
        self.game_grid.game_over.connect(self._on_game_over)
        self.game_grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.game_grid, stretch=1)
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
        records_button = QPushButton("🏆 Таблица рекордов")
        records_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        records_button.clicked.connect(self._show_records)
        layout.addWidget(records_button)
        self.tabs.addTab(game_widget, " Игра")

    def _new_game(self):
        self.game_grid.reset_board()
        self.lives_label.setText("❤️❤️❤️")
        self.timer_label.setText("Время: 00:00")
        difficulty_index = self.difficulty_combo.currentIndex()
        difficulty_map = {0: 'easy', 1: 'medium', 2: 'hard'}
        difficulty = difficulty_map[difficulty_index]
        puzzle, solution = generate_sudoku(difficulty)
        self.game_grid.set_board(puzzle, solution, is_game_mode=True)
        for row in range(9):
            for col in range(9):
                if puzzle[row][col] != 0:
                    self.game_grid.fixed[row][col] = True
        self.game_grid.update()
        self._start_timer()
        QMessageBox.information(
            self, 
            "Новая игра", 
            f"Сгенерирована новая игра!\nУровень: {self.difficulty_combo.currentText()}\n\nУ вас есть 3 жизни. Удачи!"
        )

    def _start_timer(self):
        if self.game_timer is None:
            self.game_timer = QTimer()
            self.game_timer.timeout.connect(self._update_timer)
        self.game_start_time = QTime.currentTime()
        self.game_timer.start(1000)

    def _update_timer(self):
        if self.game_start_time:
            elapsed = self.game_start_time.secsTo(QTime.currentTime())
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.setText(f"Время: {minutes:02d}:{seconds:02d}")

    def _on_error_made(self, lives_left):
        hearts = "❤️" * lives_left + "🖤" * (3 - lives_left)
        self.lives_label.setText(hearts)
        if lives_left <= 0:
            if self.game_timer:
                self.game_timer.stop()
            QMessageBox.critical(
                self,
                "Игра окончена",
                "Вы сделали 3 ошибки\n\nХотите начать новую игру?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
        else:
            QMessageBox.warning(
                self,
                "Ошибка!",
                f"Неправильная цифра!\nОсталось жизней: {lives_left}"
            )

    def _on_game_over(self, is_win):
        if self.game_timer:
            self.game_timer.stop()
        if is_win:
            elapsed = self.game_start_time.secsTo(QTime.currentTime())
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"{minutes}:{seconds:02d}"
            dialog = QDialog(self)
            dialog.setWindowTitle("Победа!")
            layout = QVBoxLayout(dialog)
            msg = QLabel(f" Поздравляем! Вы решили судоку!\nВремя: {time_str}")
            msg.setStyleSheet("font-size: 16px;")
            layout.addWidget(msg)
            layout.addWidget(QLabel("Введите ваше имя для таблицы рекордов:"))
            name_input = QLineEdit()
            name_input.setPlaceholderText("Ваше имя")
            layout.addWidget(name_input)
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            if dialog.exec() == QDialog.Accepted:
                player_name = name_input.text() or "Аноним"
                difficulty = self.difficulty_combo.currentText()
                self._save_record(player_name, difficulty, elapsed)
            QMessageBox.information(self, "Победа!", "Отличная работа!")

    def _save_record(self, name, difficulty, time_seconds):
        records_file = "records.json"
        records = []
        if os.path.exists(records_file):
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                records = []
        records.append({
            "name": name,
            "difficulty": difficulty,
            "time": time_seconds
        })
        records.sort(key=lambda x: x["time"])
        records = records[:15]
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def _show_records(self):
        records_file = "records.json"
        dialog = QDialog(self)
        dialog.setWindowTitle("🏆 Таблица рекордов")
        dialog.resize(400, 400)
        layout = QVBoxLayout(dialog)
        if not os.path.exists(records_file):
            layout.addWidget(QLabel("Пока нет рекордов. Будьте первым!"))
        else:
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                list_widget = QListWidget()
                for i, record in enumerate(records, 1):
                    minutes = record["time"] // 60
                    seconds = record["time"] % 60
                    time_str = f"{minutes}:{seconds:02d}"
                    item = QListWidgetItem(
                        f"{i}. {record['name']} - {record['difficulty']} - {time_str}"
                    )
                    list_widget.addItem(item)
                layout.addWidget(list_widget)
            except:
                layout.addWidget(QLabel("Ошибка загрузки рекордов"))
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        dialog.exec()

    def _check_solution(self):
        if self.game_grid.solution is None:
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
        if current_board == self.game_grid.solution:
            if self.game_timer:
                self.game_timer.stop()
            QMessageBox.information(
                self, 
                "Поздравляем!", 
                "🎉 Вы решили судоку правильно!\n\nОтличная работа!"
            )
        else:
            QMessageBox.warning(
                self, 
                "Неверно", 
                "Решение неверное.\n\nПроверьте свои ответы!"
            )

    def _create_solver_tab(self):
        solver_widget = QWidget()
        layout = QVBoxLayout(solver_widget)
        self.sudoku_grid = SudokuWidget()
        self.sudoku_grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.sudoku_grid, stretch=1)
        solve_button = QPushButton(" Решить")
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
        clear_button = QPushButton("🗑️ Очистить")
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
        self.tabs.addTab(solver_widget, " Решатель")

    def _solve_sudoku(self):
        board = self.sudoku_grid.get_board()
        if not is_valid_board(board):
            QMessageBox.critical(
                self,
                "Ошибка ввода",
                "Исходные данные нарушают правила судоку!\n\n"
                "Проверьте, нет ли повторяющихся цифр."
            )
            return
        if solve(board):
            self.sudoku_grid.set_board(board)
            QMessageBox.information(self, "Успех", "Судоку решено!")
        else:
            QMessageBox.warning(self, "Ошибка", "Решение не найдено.")

    def _clear_board(self):
        self.sudoku_grid.reset_board()

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
            "<h3>Судоку: Игра и Решатель</h3>"
            "<p><b>Цель игры:</b> Заполнить сетку 9x9.</p>"
            "<p><b>Правила:</b> В каждой строке, столбце и блоке 3x3 должны быть цифры 1-9.</p>"
            "<p><b>Управление:</b> Кликните на клетку и введите цифру (1-9).</p>"
            "<p><b>Ошибки:</b> У вас есть 3 жизни. Неправильная цифра = минус жизнь!</p>"
        )

    def save_profile(self):
        profile = {
            "window_size": [self.width(), self.height()],
            "last_difficulty": self.difficulty_combo.currentIndex()
        }
        with open("profile.json", 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

    def load_profile(self):
        if os.path.exists("profile.json"):
            try:
                with open("profile.json", 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                if "window_size" in profile:
                    self.resize(profile["window_size"][0], profile["window_size"][1])
                self.saved_difficulty = profile.get("last_difficulty", 1)
            except:
                self.saved_difficulty = 1
        else:
            self.saved_difficulty = 1

    def closeEvent(self, event):
        self.save_profile()
        event.accept()
