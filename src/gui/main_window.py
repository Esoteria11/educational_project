from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QLabel, QMenuBar, QMessageBox, QPushButton,
    QHBoxLayout, QRadioButton, QButtonGroup, QDialog, QDialogButtonBox,
    QListWidget, QListWidgetItem, QLineEdit, QSizePolicy, QGridLayout,
    QTextBrowser, QInputDialog
)
from PySide6.QtCore import Qt, QTime, QTimer
from src.gui.sudoku_widget import SudokuWidget
from src.gui.solver_widget import SolverWidget
from src.logic.solver import solve, is_valid_board
from src.logic.generator import generate_sudoku
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Судоку")
        self.resize(1100, 750)
        self.setMinimumSize(1000, 700)
        self.setMaximumSize(1600, 1200)
        self.setStyleSheet("background-color: white;")
        self.saved_difficulty = 1
        self.load_profile()
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
        self.best_time = None
        self.is_paused = False
        self.total_elapsed_seconds = 0
        self.elapsed_time_at_pause = 0
        self._create_game_tab()
        self._create_solver_tab()
        self._create_menu()
        self._apply_saved_difficulty()
        self._load_best_time()
        self._update_records_display()
        
    def _load_best_time(self):
        self._update_best_time_display()
    
    def _update_best_time_display(self):
        difficulty = self._get_difficulty_text()
        records_file = "records.json"
        
        html = f"<b>🏆 Топ-3 ({difficulty}):</b><br>"
        personal_best = None
        
        if os.path.exists(records_file):
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        records = {}
                    else:
                        records = json.loads(content)
                
                if difficulty in records and records[difficulty]:
                    for i, rec in enumerate(records[difficulty][:3]):
                        mins, secs = divmod(rec['time'], 60)
                        time_str = f"{mins:02d}:{secs:02d}"
                        if rec['name'] == self.player_name:
                            html += f"<span style='color: #0066ff; font-weight: bold;'>{i+1}. {rec['name']} — {time_str}</span><br>"
                        else:
                            html += f"{i+1}. {rec['name']} — {time_str}<br>"
                    
                    for rec in records[difficulty]:
                        if rec['name'] == self.player_name:
                            personal_best = rec['time']
                            break
            except (json.JSONDecodeError, KeyError):
                pass
                
        if personal_best is not None:
            mins, secs = divmod(personal_best, 60)
            html += f"<br><b>Ваш рекорд:</b> {mins:02d}:{secs:02d}"
        else:
            html += "<br><i style='color: #9e9e9e;'>У вас пока нет рекордов</i>"
            
        self.records_label.setText(html)

    def _update_records_display(self):
        difficulty = self._get_difficulty_text()
        records_file = "records.json"
        
        html = f"<b>🏆 Топ-3 ({difficulty}):</b><br>"
        personal_best = None
        
        if os.path.exists(records_file):
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                
                if difficulty in records and records[difficulty]:
                    for i, rec in enumerate(records[difficulty][:3]):
                        mins, secs = divmod(rec['time'], 60)
                        time_str = f"{mins:02d}:{secs:02d}"
                        if rec['name'] == self.player_name:
                            html += f"<span style='color: #0066ff; font-weight: bold;'>{i+1}. {rec['name']} — {time_str}</span><br>"
                        else:
                            html += f"{i+1}. {rec['name']} — {time_str}<br>"
                    
                    for rec in records[difficulty]:
                        if rec['name'] == self.player_name:
                            personal_best = rec['time']
                            break
            except:
                pass
                
        if personal_best is not None:
            mins, secs = divmod(personal_best, 60)
            html += f"<br><b>Ваш рекорд:</b> {mins:02d}:{secs:02d}"
        else:
            html += "<br><i style='color: #9e9e9e;'>У вас пока нет рекордов</i>"
            
        self.records_label.setText(html)
                
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
        main_layout.setSpacing(40)
        main_layout.setContentsMargins(15, 40, 40, 40)
        
        left_panel = QWidget()
        left_panel.setMaximumWidth(700)
        left_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        
        self.records_label = QLabel()
        self.records_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.records_label.setStyleSheet("font-size: 14px; color: #424242; line-height: 1.5;")
        self.records_label.setWordWrap(True)
        top_layout.addWidget(self.records_label)
        top_layout.addStretch()
        
        level_label = QLabel("Уровень:")
        level_label.setStyleSheet("font-size: 22px; color: #424242; font-weight: bold;")
        top_layout.addWidget(level_label)
        
        self.difficulty_group = QButtonGroup()
        self.easy_radio = QRadioButton("Лёгкий")
        self.medium_radio = QRadioButton("Средний")
        self.hard_radio = QRadioButton("Сложный")
        
        for radio in (self.easy_radio, self.medium_radio, self.hard_radio):
            radio.setStyleSheet("""
                QRadioButton {
                    color: #424242;
                    font-size: 18px;
                    spacing: 6px;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
            self.difficulty_group.addButton(radio)
            top_layout.addWidget(radio)
            radio.toggled.connect(self.save_profile)
            radio.toggled.connect(self._update_best_time_display)
            radio.toggled.connect(self._update_records_display)

        self.medium_radio.setChecked(True)
        left_layout.addLayout(top_layout)
        
        self.game_grid = SudokuWidget()
        self.game_grid.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.game_grid.error_made.connect(self._on_error_made)
        self.game_grid.game_over.connect(self._on_game_over)
        self.game_grid.hints_used.connect(self._on_hints_used)
        self.game_grid.board_changed.connect(self._update_remaining_numbers)
        left_layout.addWidget(self.game_grid, stretch=1, alignment=Qt.AlignCenter)

        main_layout.addWidget(left_panel, stretch=2)
        
        right_panel = QWidget()
        right_panel.setMinimumWidth(280)
        right_panel.setMaximumWidth(320)
        right_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 20, 0, 20)
        right_layout.setSpacing(25)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(40)
        stats_layout.addSpacing(70)

        time_widget = QWidget()
        time_layout = QVBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(2)
        self.time_value_label = QLabel("00:00")
        self.time_value_label.setStyleSheet("font-size: 32px; color: #424242; font-weight: bold;")
        self.time_value_label.setAlignment(Qt.AlignCenter)
        time_title_label = QLabel("Время")
        time_title_label.setStyleSheet("font-size: 18px; color: #757575;")
        time_title_label.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(self.time_value_label)
        time_layout.addWidget(time_title_label)
        stats_layout.addWidget(time_widget)

        errors_widget = QWidget()
        errors_layout = QVBoxLayout(errors_widget)
        errors_layout.setContentsMargins(0, 0, 0, 0)
        errors_layout.setSpacing(2)
        self.errors_value_label = QLabel("0/3")
        self.errors_value_label.setStyleSheet("font-size: 32px; color: #424242; font-weight: bold;")
        self.errors_value_label.setAlignment(Qt.AlignCenter)
        errors_title_label = QLabel("Ошибки")
        errors_title_label.setStyleSheet("font-size: 18px; color: #757575;")
        errors_title_label.setAlignment(Qt.AlignCenter)
        errors_layout.addWidget(self.errors_value_label)
        errors_layout.addWidget(errors_title_label)
        stats_layout.addWidget(errors_widget)
        stats_layout.addStretch()
        right_layout.addLayout(stats_layout)
        
        tools_layout = QHBoxLayout()
        tools_layout.setSpacing(15)
        tools_layout.addSpacing(30)
        
        undo_btn = QPushButton("↺")
        undo_btn.setToolTip("Отмена")
        undo_btn.setFixedSize(75, 65)
        undo_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                border-radius: 12px;
                font-size: 28px;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        undo_btn.clicked.connect(self._undo)
        tools_layout.addWidget(undo_btn)
        
        clear_btn = QPushButton("⌫")
        clear_btn.setToolTip("Очистить")
        clear_btn.setFixedSize(75, 65)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                border-radius: 12px;
                font-size: 26px;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        clear_btn.clicked.connect(self._clear_cell)
        tools_layout.addWidget(clear_btn)

        hint_container = QWidget()
        hint_container_layout = QHBoxLayout(hint_container)
        hint_container_layout.setContentsMargins(0, 0, 0, 0)
        hint_container_layout.setSpacing(0)
        
        self.hint_button = QPushButton("💡")
        self.hint_button.setToolTip("Подсказка")
        self.hint_button.setFixedSize(75, 65)
        self.hint_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                border-radius: 12px;
                font-size: 26px;
                color: #424242;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.hint_button.clicked.connect(self._use_hint)
        hint_container_layout.addWidget(self.hint_button)
        
        self.hint_badge = QLabel("3")
        self.hint_badge.setStyleSheet("""
            QLabel {
                background-color: #2979ff;
                color: white;
                border-radius: 9px;
                font-size: 11px;
                font-weight: bold;
                min-width: 18px;
                min-height: 18px;
                max-width: 18px;
                max-height: 18px;
                padding: 0px;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.hint_badge.setAlignment(Qt.AlignCenter)
        badge_widget = QWidget()
        badge_widget.setFixedSize(18, 18)
        badge_layout = QHBoxLayout(badge_widget)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.addWidget(self.hint_badge)
        hint_container_layout.addWidget(badge_widget)
        hint_container_layout.addStretch()
        
        tools_layout.addWidget(hint_container)
        tools_layout.addStretch()
        right_layout.addLayout(tools_layout)
        
        number_grid = QGridLayout()
        number_grid.setSpacing(12)
        self.number_buttons = []
        
        for i in range(1, 10):
            row = (i - 1) // 3
            col = (i - 1) % 3
            btn = QPushButton(str(i))
            btn.setFixedSize(100, 90)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f5f7fa;
                        border: none;
                        border-radius: 10px;
                        font-size: 36px;
                        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                        font-weight: 300;
                        color: #0066ff;
                    }
                    QPushButton:hover {
                        background-color: #e3f2fd;
                    }
                    QPushButton:pressed {
                        background-color: #bbdefb;
                    }
                """)
            btn.clicked.connect(lambda checked, num=i: self._input_number(num))
            number_grid.addWidget(btn, row, col)
            self.number_buttons.append(btn)
        
        right_layout.addLayout(number_grid)
        right_layout.addStretch()

        solver_buttons_layout = QVBoxLayout()
        solver_buttons_layout.setSpacing(10)
        
        send_to_solver_btn = QPushButton("📤 Скопировать в решатель")
        send_to_solver_btn.setFixedHeight(50)
        send_to_solver_btn.setToolTip("Скопировать текущее поле игры во вкладку Решателя")
        send_to_solver_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f7fa;
                color: #424242;
                font-size: 13px;
                padding: 8px 15px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
            }
        """)
        send_to_solver_btn.clicked.connect(self._send_to_solver)
        solver_buttons_layout.addWidget(send_to_solver_btn)
        
        show_solution_btn = QPushButton("✅ Показать Решение")
        show_solution_btn.setFixedHeight(50)
        show_solution_btn.setToolTip("Показать правильное решение в решателе")
        show_solution_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f7fa;
                color: #424242;
                font-size: 13px;
                padding: 8px 15px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
            }
        """)
        show_solution_btn.clicked.connect(self._show_solution)
        solver_buttons_layout.addWidget(show_solution_btn)
        
        right_layout.addLayout(solver_buttons_layout)
        
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #e0e0e0; margin: 10px 0;")
        right_layout.addWidget(separator)
        
        new_game_btn = QPushButton("Новая игра")
        new_game_btn.setMinimumHeight(40)
        new_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c7cda;
                color: white;
                font-size: 17px;
                padding: 15px 30px;
                border: none;
                border-radius: 10px;
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
        layout.setContentsMargins(40, 40, 40, 40)
        
        self.solver_grid = SolverWidget()
        layout.addWidget(self.solver_grid, stretch=1, alignment=Qt.AlignCenter)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        solve_btn = QPushButton("Решить пошагово")
        solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #66bb6a;
                color: white;
                font-size: 16px;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #55a859;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """)
        solve_btn.clicked.connect(self._solve_sudoku)
        buttons_layout.addWidget(solve_btn)
        self.solve_btn = solve_btn
        
        clear_btn = QPushButton("Очистить")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef5350;
                color: white;
                font-size: 16px;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        clear_btn.clicked.connect(self._clear_board)
        buttons_layout.addWidget(clear_btn)
        
        layout.addLayout(buttons_layout)
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
        counts = self.game_grid.get_numbers_count()
        
        for i, btn in enumerate(self.number_buttons):
            num = i + 1
            
            if counts[num] >= 9:
                btn.setEnabled(False)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0;
                        border: none;
                        border-radius: 10px;
                        font-size: 32px;
                        color: #9e9e9e;
                        font-weight: normal;
                    }
                """)
            else:
                btn.setEnabled(True)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f5f7fa;
                        border: none;
                        border-radius: 10px;
                        font-size: 36px;
                        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                        font-weight: 300;
                        color: #0066ff;
                    }
                    QPushButton:hover {
                        background-color: #e3f2fd;
                    }
                    QPushButton:pressed {
                        background-color: #bbdefb;
                    }
                """)
            
    def _input_number(self, num):
        if self.game_grid.selected_cell and not self.game_grid.is_game_over:
            row, col = self.game_grid.selected_cell
            if not self.game_grid.fixed[row][col]:
                self.game_grid._try_set_number(row, col, num)
        self.game_grid.setFocus()
                
    def _new_game(self):
        self.game_grid.reset_board()
        self.time_value_label.setText("00:00")
        self.total_elapsed_seconds = 0
        self.errors_value_label.setText("0/3")
        
        difficulty = self._get_difficulty()
        puzzle, solution = generate_sudoku(difficulty)
        
        self.game_grid.set_board(puzzle, solution, is_game_mode=True)
        
        for row in range(9):
            for col in range(9):
                if puzzle[row][col] != 0:
                    self.game_grid.fixed[row][col] = True
        
        self.game_grid.update()
        self._start_timer()
        self._update_remaining_numbers()
        
        self.hint_button.setEnabled(True)
        self.hint_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                border-radius: 12px;
                font-size: 26px;
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
                border-radius: 9px;
                font-size: 11px;
                font-weight: bold;
                min-width: 18px;
                min-height: 18px;
                max-width: 18px;
                max-height: 18px;
                qproperty-alignment: AlignCenter;
            }
        """)
        
    def _undo(self):
        self.game_grid.undo()
        self._update_remaining_numbers()
        errors_count = 3 - self.game_grid.lives
        self.errors_value_label.setText(f"{errors_count}/3")
        self.game_grid.setFocus()
        
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
                self.errors_value_label.setText(f"{errors_count}/3")
                self.game_grid.setFocus()
                
    def _use_hint(self):
        if not self.game_grid.selected_cell:
            QMessageBox.information(self, "Подсказка", "Сначала выберите клетку!")
            return
        if self.game_grid.use_hint():
            self._update_remaining_numbers()
            self.hint_badge.setText(str(self.game_grid.hints_remaining))
            if self.game_grid.hints_remaining == 0:
                self.hint_button.setEnabled(False)
                self.hint_button.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0;
                        border: none;
                        border-radius: 12px;
                        font-size: 26px;
                        color: #9e9e9e;
                    }
                """)
        self.game_grid.setFocus()
                
    def _on_hints_used(self, remaining):
        self.hint_badge.setText(str(remaining))
        if remaining == 0:
            self.hint_button.setEnabled(False)
            self.hint_button.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    border: none;
                    border-radius: 12px;
                    font-size: 26px;
                    color: #9e9e9e;
                }
            """)
            
    def _start_timer(self):
        if self.game_timer is None:
            self.game_timer = QTimer()
            self.game_timer.timeout.connect(self._update_timer)
        self.total_elapsed_seconds = 0
        self.game_timer.start(1000)
        
    def _update_timer(self):
        self.total_elapsed_seconds += 1
        minutes = self.total_elapsed_seconds // 60
        seconds = self.total_elapsed_seconds % 60
        self.time_value_label.setText(f"{minutes:02d}:{seconds:02d}")
            
    def _on_error_made(self, lives_left):
        errors_count = 3 - lives_left
        self.errors_value_label.setText(f"{errors_count}/3")
        if lives_left <= 0:
            if self.game_timer:
                self.game_timer.stop()
                
            dialog = QDialog(self)
            dialog.setWindowTitle("Игра окончена")
            dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                    color: black;
                }
                QLabel {
                    color: black;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #5c7cda;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #4267c7;
                }
                QPushButton#noBtn {
                    background-color: #ef5350;
                }
                QPushButton#noBtn:hover {
                    background-color: #e53935;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(20)
            
            msg_label = QLabel("Вы сделали 3 ошибки.\nНачать новую игру?")
            msg_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(msg_label)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            
            yes_btn = QPushButton("Да")
            yes_btn.clicked.connect(dialog.accept)
            
            no_btn = QPushButton("Нет")
            no_btn.setObjectName("noBtn")
            no_btn.clicked.connect(dialog.reject)
            
            btn_layout.addWidget(yes_btn)
            btn_layout.addWidget(no_btn)
            btn_layout.addStretch()
            
            layout.addLayout(btn_layout)
            
            if dialog.exec() == QDialog.Accepted:
                self._new_game()
                
    def _on_game_over(self, is_win):
        if self.game_timer:
            self.game_timer.stop()
        if is_win:
            elapsed = self.total_elapsed_seconds
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"{minutes}:{seconds:02d}"
            
            if self.best_time is None or elapsed < self.best_time:
                self.best_time = elapsed
                self._update_records_display()
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Победа!")
            dialog.resize(450, 300)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                    color: black;
                }
                QLabel {
                    color: black;
                    font-size: 18px;
                }
                QLineEdit {
                    background-color: white;
                    color: black;
                    border: 1px solid #ccc;
                    padding: 10px;
                    font-size: 16px;
                    border-radius: 4px;
                }
                QPushButton {
                    background-color: #5c7cda;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 4px;
                    font-size: 16px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #4267c7;
                }
                QPushButton#cancelBtn {
                    background-color: #9e9e9e;
                }
                QPushButton#cancelBtn:hover {
                    background-color: #757575;
                }
            """)
            layout = QVBoxLayout(dialog)
            layout.setSpacing(20)
            
            msg = QLabel(f"🎉 Поздравляем! Вы решили судоку!\nВремя: {time_str}")
            msg.setAlignment(Qt.AlignCenter)
            layout.addWidget(msg)
            
            name_label = QLabel("Введите ваше имя для таблицы рекордов:")
            name_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(name_label)
            
            name_input = QLineEdit()
            name_input.setPlaceholderText("Ваше имя")
            name_input.setText(self.player_name)
            layout.addWidget(name_input)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            
            save_btn = QPushButton("Сохранить")
            save_btn.clicked.connect(dialog.accept)
            
            cancel_btn = QPushButton("Отмена")
            cancel_btn.setObjectName("cancelBtn")
            cancel_btn.clicked.connect(dialog.reject)
            
            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(cancel_btn)
            btn_layout.addStretch()
            
            layout.addLayout(btn_layout)
            
            if dialog.exec() == QDialog.Accepted:
                player_name = name_input.text().strip() or "Игрок"
                
                if player_name != self.player_name:
                    self.player_name = player_name
                    self.save_profile() 
                    
                difficulty = self._get_difficulty_text()
                self._save_record(player_name, difficulty, elapsed)
                self._update_records_display()
                
    def _save_record(self, name, difficulty, time_seconds):
        records_file = "records.json"
        records = {}
        
        if os.path.exists(records_file):
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                records = {}
        
        if difficulty not in records:
            records[difficulty] = []
        
        records[difficulty].append({
            "name": name, 
            "time": time_seconds
        })
        
        records[difficulty].sort(key=lambda x: x["time"])
        records[difficulty] = records[difficulty][:15]
        
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
            
    def _show_records(self):
        records_file = "records.json"
        current_difficulty = self._get_difficulty_text()
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Таблица рекордов ({current_difficulty})")
        dialog.resize(400, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
            }
            QListWidget {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #5c7cda;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4267c7;
            }
        """)
        layout = QVBoxLayout(dialog)
        
        if not os.path.exists(records_file):
            no_records_label = QLabel(f"Пока нет рекордов для уровня {current_difficulty}. Будьте первым!")
            layout.addWidget(no_records_label)
        else:
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                
                if current_difficulty in records and records[current_difficulty]:
                    list_widget = QListWidget()
                    for i, record in enumerate(records[current_difficulty], 1):
                        minutes = record["time"] // 60
                        seconds = record["time"] % 60
                        time_str = f"{minutes}:{seconds:02d}"
                        item = QListWidgetItem(f"{i}. {record['name']} - {time_str}")
                        list_widget.addItem(item)
                    layout.addWidget(list_widget)
                else:
                    no_records_label = QLabel(f"Пока нет рекордов для уровня {current_difficulty}. Будьте первым!")
                    layout.addWidget(no_records_label)
            except:
                error_label = QLabel("Ошибка загрузки рекордов")
                layout.addWidget(error_label)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        dialog.exec()
        
    def _solve_sudoku(self):
        board = self.solver_grid.get_board()
        from src.logic.solver import solve, is_valid_board
        
        if not is_valid_board(board):
            QMessageBox.critical(self, "❌ Ошибка ввода", "Исходные данные нарушают правила судоку!")
            return
            
        board_copy = [row[:] for row in board]
        
        if not solve(board_copy):
            QMessageBox.warning(self, "❌ Ошибка", "У этого судоку нет решения.")
            return
            
        self.steps_to_animate = []
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0 and board_copy[r][c] != 0:
                    self.steps_to_animate.append((r, c, board_copy[r][c]))
                    
        self.solve_btn.setEnabled(False)
        self.animation_index = 0
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animation_step)
        self.animation_timer.start(50)

    def _animation_step(self):
        if self.animation_index < len(self.steps_to_animate):
            r, c, num = self.steps_to_animate[self.animation_index]
            self.solver_grid.set_cell(r, c, num)
            self.animation_index += 1
        else:
            self.animation_timer.stop()
            self.solve_btn.setEnabled(True)
            QMessageBox.information(self, "✅ Успех", "Судоку решено!")
        
    def _clear_board(self):
        self.solver_grid.clear_board()
        self.solve_btn.setEnabled(True)
        
    def _create_menu(self):
        self.setStyleSheet("""
            QMenuBar {
                background-color: white;
                color: #424242;
                border-bottom: 1px solid #e0e0e0;
                padding: 2px;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #424242;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QMenuBar::item:selected {
                background-color: #e3f2fd;
                color: #424242;
            }
            QMenuBar::item:pressed {
                background-color: #bbdefb;
                color: #424242;
            }
            QMenu {
                background-color: white;
                color: #424242;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 5px 0;
            }
            QMenu::item {
                padding: 8px 25px;
                color: #424242;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #424242;
            }
            QMenu::separator {
                height: 1px;
                background: #e0e0e0;
                margin: 5px 10px;
            }
        """)
        
        menu_bar = self.menuBar()
        
        game_menu = menu_bar.addMenu("Игра")
        
        pause_action = game_menu.addAction("⏸ Пауза")
        pause_action.triggered.connect(self._toggle_pause)
        pause_action.setShortcut("Esc")
        
        game_menu.addSeparator()
        
        exit_action = game_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)
        
        help_menu = menu_bar.addMenu("Справка")
        
        help_action = help_menu.addAction("Помощь")
        help_action.triggered.connect(self._show_help)
        
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self.show_about_dialog)
        
    def show_about_dialog(self):
        about_text = (
            "<h2>Судоку: Игра и Решатель</h2>"
            "<p><b>Описание:</b></p>"
            "<p>Классическая игра Судоку со встроенным решателем."
            "<p><b>Возможности:</b></p>"
            "<ul>"
            "<li>Три уровня сложности: лёгкий, средний, сложный</li>"
            "<li>Таблица рекордов</li>"
            "<li>Система подсказок и режим заметок</li>"
            "<li>Встроенный решатель</li>"
            "<li>Сохранение профиля игрока</li>"
            "</ul>"
            "<p><b>Технологии:</b> Python, PySide6 (Qt)</p>"
            "<p><b>Автор:</b> Ким Денис, Томский политехнический университет, «Программная инженерия», 1 курс бакалавриата</p>"
            "<b>Учебная практика по развитию цифровых компетенций, 2026 г.<br>"
        )
        
        dialog = QDialog(self)
        dialog.setWindowTitle("О программе")
        dialog.resize(550, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                color: black;
            }
            QTextBrowser {
                background-color: white;
                color: black;
                border: none;
                font-size: 18px;
            }
            QPushButton {
                background-color: #5c7cda;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4267c7;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        text_browser = QTextBrowser()
        text_browser.setHtml(about_text)
        layout.addWidget(text_browser)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()

    def _show_help(self):
        help_text = """
        <h2>Как играть в Судоку?</h2>
        
        <h3>Цель игры:</h3>
        <p>Заполнить пустые клетки цифрами от 1 до 9 так, чтобы в каждой строке, 
        каждом столбце и каждом квадрате 3x3 каждая цифра встречалась только один раз.</p>
        
        <h3>Управление:</h3>
        <ul>
            <li><b> Мышь:</b> нажмите на клетку для выбора</li>
            <li><b> Клавиатура:</b> цифры 1-9 для ввода</li>
            <li><b> Backspace/Delete:</b> удалить цифру из клетки</li>
            <li><b> Стрелки:</b> перемещение между клетками</li>
            <li><b> Esc:</b> пауза</li>
        </ul>
        
        <h3>Элементы интерфейса:</h3>
        <ul>
            <li><b> ↺ Отмена:</b> отменить последнее действие</li>
            <li><b> ⌫ Очистить:</b> удалить цифру из выбранной клетки</li>
            <li><b> 💡 Подсказка:</b> показать правильную цифру в выбранной клетке (максиум 3 подсказки)</li>
        </ul>
        
        <h3></h3>
        <ul>
            <li> У вас есть 3 жизни</li>
            <li> При 3 ошибках игра заканчивается</li>
            <li> Развивайтесь и устанавливайте новые рекорды!</li>
        </ul>
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Помощь")
        dialog.resize(600, 500)

        dialog.setStyleSheet("""
        QDialog {
            background-color: white;
            color: black;
            font-family: Arial, sans-serif;
        }
        QTextBrowser {
            background-color: white;
            color: black;
            border: none;
            font-size: 18px;
        }
        QPushButton {
            background-color: #5c7cda;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            font-size: 18px;
        }
        QPushButton:hover {
            background-color: #4267c7;
        }
    """)
        
        layout = QVBoxLayout(dialog)
        
        text_browser = QTextBrowser()
        text_browser.setHtml(help_text)
        layout.addWidget(text_browser)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()

    def _copy_to_solver(self):
        """Вспомогательный метод: копирует состояние игры в решатель"""
        board = self.game_grid.get_board()
        self.solver_grid.clear_board()
        
        for row in range(9):
            for col in range(9):
                if board[row][col] != 0:
                    self.solver_grid.board[row][col] = board[row][col]
                    self.solver_grid.initial_board[row][col] = board[row][col]
        
        self.solver_grid.update()

    def _send_to_solver(self):
        self._copy_to_solver()
        self.tabs.setCurrentIndex(1)
        self.game_grid.setFocus()
            
    def _show_solution(self):
        self._copy_to_solver()
        
        board = self.solver_grid.get_board()
        from src.logic.solver import solve, is_valid_board
        
        if not is_valid_board(board):
            QMessageBox.critical(
                self, 
                "❌ Ошибка", 
                "Текущее состояние поля нарушает правила судоку. Невозможно показать решение."
            )
            self.game_grid.setFocus()
            return
            
        board_copy = [row[:] for row in board]
        
        if not solve(board_copy):
            QMessageBox.warning(self, "❌ Ошибка", "У этого судоку нет решения.")
            self.game_grid.setFocus()
            return
            
        self.steps_to_animate = []
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0 and board_copy[r][c] != 0:
                    self.steps_to_animate.append((r, c, board_copy[r][c]))
                    
        self.tabs.setCurrentIndex(1)
        
        self.solve_btn.setEnabled(False)
        self.animation_index = 0
        
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
            
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animation_step)
        self.animation_timer.start(50)
        
        self.game_grid.setFocus()

    def _toggle_pause(self):
        if not self.game_timer or not self.game_timer.isActive():
            return
        if self.is_paused:
            return
            
        self.is_paused = True
        self.game_timer.stop()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Пауза")
        dialog.resize(300, 150)
        dialog.setStyleSheet("""
            QDialog { 
                background-color: white; 
                color: black; 
            }
            QLabel { 
                font-size: 22px; 
                color: #424242; 
                font-weight: bold; 
            }
            QPushButton { 
                background-color: #5c7cda; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                border-radius: 4px; 
                font-size: 16px; 
            }
            QPushButton:hover { 
                background-color: #4267c7; 
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        
        msg = QLabel("⏸ Игра на паузе")
        msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg)
        
        resume_btn = QPushButton("Продолжить")
        resume_btn.clicked.connect(dialog.accept)
        layout.addWidget(resume_btn)
        
        dialog.exec()
        
        self.is_paused = False
        self.game_timer.start(1000)
        
    def save_profile(self):
        difficulty = 1
        if hasattr(self, 'easy_radio'):
            if self.easy_radio.isChecked(): difficulty = 0
            elif self.hard_radio.isChecked(): difficulty = 2
        
        profile = {
            "window_size": [self.width(), self.height()], 
            "last_difficulty": difficulty,
            "player_name": getattr(self, 'player_name', 'Игрок')
        }
        with open("profile.json", 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
            
    def load_profile(self):
        self.player_name = "Игрок"
        
        if os.path.exists("profile.json"):
            try:
                with open("profile.json", 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        profile = json.loads(content)
                        if "window_size" in profile:
                            self.resize(profile["window_size"][0], profile["window_size"][1])
                        self.saved_difficulty = profile.get("last_difficulty", 1)
                        
                        saved_name = profile.get("player_name", "")
                        if saved_name and saved_name.strip():
                            self.player_name = saved_name.strip()
            except:
                pass
            
    def closeEvent(self, event):
        self.save_profile()
        event.accept()
