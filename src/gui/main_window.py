from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QLabel, QMenuBar, QMessageBox, QPushButton,
    QHBoxLayout, QRadioButton, QButtonGroup, QDialog, QDialogButtonBox,
    QListWidget, QListWidgetItem, QLineEdit, QSizePolicy, QGridLayout
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
        self.resize(1000, 700)
        self.setStyleSheet("background-color: white;")
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: none;
            }
            QTabBar::tab {
                background-color: white;
                color: #424242;
                padding: 10px 20px;
                border: none;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                border-bottom: 2px solid #2979ff;
                color: #2979ff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #f5f5f5;
            }
        """)
        self.setCentralWidget(self.tabs)
        self.game_timer = None
        self.game_start_time = None
        self.saved_difficulty = 1
        self.best_time = None
        self._create_game_tab()
        self._create_solver_tab()
        self._create_menu()
        self._apply_saved_difficulty()
        self._load_best_time()
        
    def _load_best_time(self):
        records_file = "records.json"
        if os.path.exists(records_file):
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                if records:
                    self.best_time = records[0]['time']
                    minutes = self.best_time // 60
                    seconds = self.best_time % 60
                    self.best_time_label.setText(f"{minutes:02d}:{seconds:02d}")
            except:
                pass
                
    def _apply_saved_difficulty(self):
        if self.saved_difficulty == 0:
            self.easy_radio.setChecked(True)
        elif self.saved_difficulty == 2:
            self.hard_radio.setChecked(True)
        else:
            self.medium_radio.setChecked(True)
            
    def _create_game_tab(self):
        game_widget = QWidget()
        main_layout = QHBoxLayout(game_widget)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        top_info = QHBoxLayout()
        self.best_time_label = QLabel("00:00")
        self.best_time_label.setStyleSheet("font-size: 16px; color: #424242; font-weight: bold;")
        top_info.addWidget(QLabel("Рекорд:"))
        top_info.addWidget(self.best_time_label)
        top_info.addStretch()
        left_layout.addLayout(top_info)
        
        self.difficulty_group = QButtonGroup()
        self.easy_radio = QRadioButton("Лёгкий")
        self.medium_radio = QRadioButton("Средний")
        self.hard_radio = QRadioButton("Сложный")
        
        self.easy_radio.setStyleSheet("color: #424242; font-size: 13px;")
        self.medium_radio.setStyleSheet("color: #424242; font-size: 13px;")
        self.hard_radio.setStyleSheet("color: #424242; font-size: 13px;")
        
        self.difficulty_group.addButton(self.easy_radio, 0)
        self.difficulty_group.addButton(self.medium_radio, 1)
        self.difficulty_group.addButton(self.hard_radio, 2)
        
        diff_layout = QHBoxLayout()
        diff_layout.addWidget(QLabel("Уровень:"))
        diff_layout.addWidget(self.easy_radio)
        diff_layout.addWidget(self.medium_radio)
        diff_layout.addWidget(self.hard_radio)
        left_layout.addLayout(diff_layout)
        
        left_layout.addStretch()
        
        self.game_grid = SudokuWidget()
        self.game_grid.error_made.connect(self._on_error_made)
        self.game_grid.game_over.connect(self._on_game_over)
        self.game_grid.hints_used.connect(self._on_hints_used)
        self.game_grid.board_changed.connect(self._update_remaining_numbers)
        self.game_grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.addWidget(self.game_grid, stretch=1)
        
        numbers_layout = QHBoxLayout()
        numbers_layout.setSpacing(5)
        self.remaining_number_buttons = []
        for i in range(1, 10):
            btn = QPushButton(str(i))
            btn.setFixedSize(40, 50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid #2979ff;
                    border-radius: 8px;
                    font-size: 24px;
                    color: #2979ff;
                    font-weight: bold;
                }
                QPushButton:disabled {
                    border: 2px solid #e0e0e0;
                    color: #e0e0e0;
                }
            """)
            btn.setEnabled(False)
            numbers_layout.addWidget(btn)
            self.remaining_number_buttons.append(btn)
        
        left_layout.addLayout(numbers_layout)
        
        main_layout.addWidget(left_panel, stretch=2)
        
        right_panel = QWidget()
        right_panel.setMaximumWidth(300)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 20, 20, 20)
        
        top_stats = QHBoxLayout()
        self.errors_label = QLabel("Ошибки\n1/3")
        self.errors_label.setStyleSheet("font-size: 18px; color: #424242;")
        self.errors_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        top_stats.addWidget(self.errors_label)
        top_stats.addStretch()
        self.timer_label = QLabel("Время\n00:00")
        self.timer_label.setStyleSheet("font-size: 18px; color: #424242;")
        self.timer_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        top_stats.addWidget(self.timer_label)
        right_layout.addLayout(top_stats)
        
        icon_layout = QHBoxLayout()
        
        undo_btn = QPushButton("↺")
        undo_btn.setToolTip("Отмена")
        undo_btn.setFixedSize(60, 60)
        undo_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                border-radius: 30px;
                font-size: 24px;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        undo_btn.clicked.connect(self._undo)
        icon_layout.addWidget(undo_btn)
        
        clear_btn = QPushButton("⌫")
        clear_btn.setToolTip("Очистить")
        clear_btn.setFixedSize(60, 60)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                border-radius: 30px;
                font-size: 24px;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        clear_btn.clicked.connect(self._clear_cell)
        icon_layout.addWidget(clear_btn)
        
        icon_layout.addStretch()
        
        hint_btn = QPushButton("")
        hint_btn.setToolTip("Подсказка")
        hint_btn.setFixedSize(60, 60)
        hint_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                border-radius: 30px;
                font-size: 24px;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        hint_btn.clicked.connect(self._use_hint)
        icon_layout.addWidget(hint_btn)
        self.hint_button = hint_btn
        self.hint_badge = QLabel("3")
        self.hint_badge.setStyleSheet("""
            QLabel {
                background-color: #2979ff;
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        icon_layout.addWidget(self.hint_badge)
        
        right_layout.addLayout(icon_layout)
        
        number_grid = QGridLayout()
        number_grid.setSpacing(10)
        self.number_buttons = []
        for i in range(1, 10):
            row = (i - 1) // 3
            col = (i - 1) % 3
            btn = QPushButton(str(i))
            btn.setFixedSize(80, 70)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f5f7fa;
                    border: none;
                    border-radius: 8px;
                    font-size: 28px;
                    color: #2979ff;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                }
            """)
            btn.clicked.connect(lambda checked, num=i: self._input_number(num))
            number_grid.addWidget(btn, row, col)
            self.number_buttons.append(btn)
        
        right_layout.addLayout(number_grid)
        right_layout.addStretch()
        
        new_game_btn = QPushButton("Новая игра")
        new_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c7cda;
                color: white;
                font-size: 16px;
                padding: 15px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4267c7;
            }
        """)
        new_game_btn.clicked.connect(self._new_game)
        right_layout.addWidget(new_game_btn)
        
        main_layout.addWidget(right_panel, stretch=1)
        
        self.tabs.addTab(game_widget, "Игра")
        
    def _create_solver_tab(self):
        solver_widget = QWidget()
        layout = QVBoxLayout(solver_widget)
        self.sudoku_grid = SudokuWidget()
        self.sudoku_grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.sudoku_grid, stretch=1)
        
        solve_btn = QPushButton("Решить")
        solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #66bb6a;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 4px;
            }
        """)
        solve_btn.clicked.connect(self._solve_sudoku)
        layout.addWidget(solve_btn)
        
        clear_btn = QPushButton("Очистить")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef5350;
                color: white;
                font-size: 14px;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
        """)
        clear_btn.clicked.connect(self._clear_board)
        layout.addWidget(clear_btn)
        
        self.tabs.addTab(solver_widget, "Решатель")
        
    def _get_difficulty(self):
        if self.easy_radio.isChecked(): return 'easy'
        if self.hard_radio.isChecked(): return 'hard'
        return 'medium'
        
    def _get_difficulty_text(self):
        if self.easy_radio.isChecked(): return 'Лёгкий'
        if self.hard_radio.isChecked(): return 'Сложный'
        return 'Средний'
        
    def _update_remaining_numbers(self):
        remaining = self.game_grid.get_remaining_numbers()
        for i, btn in enumerate(self.remaining_number_buttons):
            num = i + 1
            if num in remaining:
                btn.setEnabled(True)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 2px solid #2979ff;
                        border-radius: 8px;
                        font-size: 24px;
                        color: #2979ff;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setEnabled(False)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 2px solid #e0e0e0;
                        border-radius: 8px;
                        font-size: 24px;
                        color: #e0e0e0;
                    }
                """)
            
    def _input_number(self, num):
        if self.game_grid.selected_cell and not self.game_grid.is_game_over:
            row, col = self.game_grid.selected_cell
            if not self.game_grid.fixed[row][col]:
                self.game_grid._try_set_number(row, col, num)
                
    def _new_game(self):
        self.game_grid.reset_board()
        self.timer_label.setText(f"Время\n00:00")
        self.errors_label.setText(f"Ошибки\n0/3")
        
        difficulty = self._get_difficulty()
        puzzle, solution = generate_sudoku(difficulty)
        
        self.game_grid.set_board(puzzle, solution, is_game_mode=True)
        self.sudoku_grid.set_board(puzzle)
        
        for row in range(9):
            for col in range(9):
                if puzzle[row][col] != 0:
                    self.game_grid.fixed[row][col] = True
                    self.sudoku_grid.fixed[row][col] = True
        
        self.game_grid.update()
        self.sudoku_grid.update()
        self._start_timer()
        self._update_remaining_numbers()
        self.hint_button.setEnabled(True)
        self.hint_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                border-radius: 30px;
                font-size: 24px;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.hint_badge.setText("3")
        self.hint_badge.setStyleSheet("""
            QLabel {
                background-color: #2979ff;
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        
    def _undo(self):
        self.game_grid.undo()
        self._update_remaining_numbers()
        errors_count = 3 - self.game_grid.lives
        self.errors_label.setText(f"Ошибки\n{errors_count}/3")
        
    def _clear_cell(self):
        if self.game_grid.selected_cell:
            row, col = self.game_grid.selected_cell
            if not self.game_grid.fixed[row][col]:
                self.game_grid.save_state()
                self.game_grid.board[row][col] = 0
                if (row, col) in self.game_grid.errors:
                    self.game_grid.errors.remove((row, col))
                self.game_grid.update()
                self._update_remaining_numbers()
                errors_count = 3 - self.game_grid.lives
                self.errors_label.setText(f"Ошибки\n{errors_count}/3")
                
    def _use_hint(self):
        if self.game_grid.use_hint():
            self._update_remaining_numbers()
            self.hint_badge.setText(str(self.game_grid.hints_remaining))
            if self.game_grid.hints_remaining == 0:
                self.hint_button.setEnabled(False)
                self.hint_button.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0;
                        border: none;
                        border-radius: 30px;
                        font-size: 24px;
                        color: #9e9e9e;
                    }
                """)
                
    def _on_hints_used(self, remaining):
        self.hint_badge.setText(str(remaining))
        if remaining == 0:
            self.hint_button.setEnabled(False)
            self.hint_button.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    border: none;
                    border-radius: 30px;
                    font-size: 24px;
                    color: #9e9e9e;
                }
            """)
            
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
            self.timer_label.setText(f"Время\n{minutes:02d}:{seconds:02d}")
            
    def _on_error_made(self, lives_left):
        errors_count = 3 - lives_left
        self.errors_label.setText(f"Ошибки\n{errors_count}/3")
        if lives_left <= 0:
            if self.game_timer:
                self.game_timer.stop()
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Игра окончена")
            msg_box.setText("Вы сделали 3 ошибки")
            msg_box.setInformativeText("Начать новую игру?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                self._new_game()
                
    def _on_game_over(self, is_win):
        if self.game_timer:
            self.game_timer.stop()
        if is_win:
            elapsed = self.game_start_time.secsTo(QTime.currentTime())
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"{minutes}:{seconds:02d}"
            
            if self.best_time is None or elapsed < self.best_time:
                self.best_time = elapsed
                self.best_time_label.setText(time_str)
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Победа!")
            layout = QVBoxLayout(dialog)
            
            msg = QLabel(f"Поздравляем! Вы решили судоку!\nВремя: {time_str}")
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
                difficulty = self._get_difficulty_text()
                self._save_record(player_name, difficulty, elapsed)
                
    def _save_record(self, name, difficulty, time_seconds):
        records_file = "records.json"
        records = []
        if os.path.exists(records_file):
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                records = []
        records.append({"name": name, "difficulty": difficulty, "time": time_seconds})
        records.sort(key=lambda x: x["time"])
        records = records[:15]
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
            
    def _show_records(self):
        records_file = "records.json"
        dialog = QDialog(self)
        dialog.setWindowTitle("Таблица рекордов")
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
                    item = QListWidgetItem(f"{i}. {record['name']} - {record['difficulty']} - {time_str}")
                    list_widget.addItem(item)
                layout.addWidget(list_widget)
            except:
                layout.addWidget(QLabel("Ошибка загрузки рекордов"))
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        dialog.exec()
        
    def _check_solution(self):
        pass
        
    def _create_solver_tab(self):
        solver_widget = QWidget()
        layout = QVBoxLayout(solver_widget)
        self.sudoku_grid = SudokuWidget()
        self.sudoku_grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.sudoku_grid, stretch=1)
        
        solve_btn = QPushButton("Решить")
        solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #66bb6a;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 4px;
            }
        """)
        solve_btn.clicked.connect(self._solve_sudoku)
        layout.addWidget(solve_btn)
        
        clear_btn = QPushButton("Очистить")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef5350;
                color: white;
                font-size: 14px;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
        """)
        clear_btn.clicked.connect(self._clear_board)
        layout.addWidget(clear_btn)
        
        self.tabs.addTab(solver_widget, "Решатель")
        
    def _solve_sudoku(self):
        board = self.sudoku_grid.get_board()
        if not is_valid_board(board):
            QMessageBox.critical(self, "Ошибка ввода", "Исходные данные нарушают правила судоку!")
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
        QMessageBox.about(self, "О программе", "Судоку: Игра и Решатель\nУчебный проект практики 1 курса.")
        
    def save_profile(self):
        difficulty = 1
        if self.easy_radio.isChecked(): difficulty = 0
        elif self.hard_radio.isChecked(): difficulty = 2
        
        profile = {"window_size": [self.width(), self.height()], "last_difficulty": difficulty}
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
