import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QMainWindow, QPushButton

class Scene(QWidget):
    def __init__(self, label, func):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel(label)
        
        button = QPushButton("Press Me!")
        button.setCheckable(True)
        button.clicked.connect(func)
        
        layout.addWidget(button)
        layout.addWidget(label)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.setCentralWidget(Scene("First scene", self.switch_to_second))

    def switch_to_second(self):
        self.setCentralWidget(Scene("Second scene", self.switch_to_first))
    
    def switch_to_first(self):
        self.setCentralWidget(Scene("First scene", self.switch_to_second))

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
