from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLabel, QMenuBar, QMessageBox
)
from PySide6.QtCore import Qt

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

        label = QLabel("Здесь будет решатель\n(Ввод данных + Алгоритм)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; color: blue;")
        layout.addWidget(label)

        self.tabs.addTab(solver_widget, "Решатель")

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
