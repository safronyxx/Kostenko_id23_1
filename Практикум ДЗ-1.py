from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer  # для цвета
import sys
import math

class Window(QMainWindow): # создаем виджет
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Circle')
        self.setGeometry(900, 300, 600, 600)
        self.radius = 200 # радиус
        self.angle = 0  # начальный угол в радианах
        self.center = (300, 300)  # центр окружности


        self.timer = QTimer(self) # таймер для обновления положения точки
        self.timer.timeout.connect(self.position) # привязываем таймер к функции обновления позиции
        self.timer.start(50)  # обновление каждые 50 мс


    def position(self): # функция обновления позиции точки на окружности
        self.angle += 0.1  # увеличиваем угол для движения по окружности
        if self.angle >= 2 * math.pi:  # если угол больше 2π, сбрасываем
            self.angle -= 2 * math.pi
        self.update()  # обновляем виджет


    def paintEvent(self, event): # рисовательная часть
        painter = QPainter(self)

        painter.setPen(QPen(Qt.darkCyan,2, Qt.SolidLine)) # окружность
        painter.drawEllipse(self.center[0] - self.radius, self.center[1] - self.radius, self.radius * 2, self.radius * 2)

        # рассчитываем координаты точки на окружности
        x = self.center[0] + self.radius * math.cos(self.angle)
        y = self.center[1] + self.radius * math.sin(self.angle)

        painter.setBrush(QBrush(Qt.blue, Qt.SolidPattern))  # точка размером 10х10
        painter.drawEllipse(x - 5, y - 5, 10, 10)


def application():
    app = QApplication(sys.argv)  # отвечает за создание приложения в целом
    window = Window()
    window.position()
    window.show()
    sys.exit(app.exec_())  # позволяет программе завершаться корректно (окно не закрывается сразу)

application()

