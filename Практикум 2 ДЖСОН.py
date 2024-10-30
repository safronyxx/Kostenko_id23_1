import sys
import random
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, QRectF, Qt
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen


# функция загрузки конфигурации из файла JSON
def load_config(filename):
    with open(filename, 'r') as file:  # r (read)
        config = json.load(file)
    return config

#  КЛАСС ПТИЧЕК
class Bird:
    def __init__(self, start_x, start_y, sit_time):
        self.x = start_x  # х стартовой позиции
        self.y = start_y  # у стартовой позиции
        self.sit_time = sit_time  # время, сколько птица сидит на столбе
        self.target_post = None  # целевой столб, куда птица хочет сесть
        self.sitting_time = 0  # текущее время, которое она сидит
        self.is_flying_away = False  # состояние "улетает ли птица"
        self.flying_speed = 3  # скорость улетания

    def move_to(self, post_x, perch_y):  # птица летит к целевой жердочке
        self.x += (post_x - self.x) * 0.05
        self.y += (perch_y - self.y) * 0.05

    def fly_away(self):  # для того чтобы птички улетали вверх
        self.y -= self.flying_speed

    def update(self, posts):  # изменение состояния птички
        if not self.is_flying_away:  # если птичка не улетает
            if self.target_post is None or not self.target_post.is_active:
                # если текущий столб упал или птица не выбрала столб, она выбирает новый/другой доступный столб
                available_posts = [post for post in posts if post.is_perch_available()] # кортеж со свободными столбами
                if available_posts: # если столб существует (доступен)
                    self.target_post = random.choice(available_posts)  # целевой пост выбираем из кортежа свободных столбов

            if self.target_post and self.target_post.is_perch_available():  # eсли птица выбрала посидеть на столбe

                # получаем координаты жердочки
                perch_x = self.target_post.x
                perch_y = self.target_post.y - self.target_post.height

                # движемся к жердочке
                self.move_to(perch_x, perch_y)

                # если птица достигла жердочки, засекаем, сколько она сидит на жердочке
                if abs(self.x - perch_x) < 5 and abs(self.y - perch_y) < 5:
                    self.sitting_time += 1

                    # если ещё не сидит, добавляем её на жердочку
                    if self.sitting_time == 1:
                        self.target_post.add_bird_to_perch()

                    # если время сидения истекло
                    if self.sitting_time >= self.sit_time:
                        self.target_post.remove_bird_from_perch() # убираем птичку со столба
                        # вероятность 50%: либо улетает, либо пересаживается на другой столб
                        if random.random() < 0.5:
                            self.is_flying_away = True # птичка улетает вверх
                        else:
                            # птичка пересаживается на другой столб
                            self.target_post = None # целевой столб снова обновляется
                            self.sitting_time = 0  # сбросываем время сидения для птички
        else:
            self.fly_away() # птица улетает вверх

            # когда птица вылетает за пределы окна, она возвращается в случайное место сверху (обновление птичек)
            if self.y < -50:
                self.is_flying_away = False
                self.target_post = None
                self.sitting_time = 0
                self.y = random.randint(-100, -50)
                self.x = random.randint(50, 750)

# КЛАСС СТОЛБОВ
class LampPost:
    def __init__(self, x, y, height, perch_capacity=5):  # максимум 5 птичек на одном столбе, иначе он падает
        self.x = x
        self.y = y
        self.height = height # высота столба
        self.perch_capacity = perch_capacity # максимальное количество птиц на жердочке
        self.current_birds = 0  # текущее количество птиц на жердочке
        self.is_active = True # состояние столба (активен или нет)
        self.recovery_timer = 0 # таймер для восстановления столба

    def is_perch_available(self): # птичка садится только на существующую жердочку, на которой есть место
        # проверяем, активен ли столб и есть ли на нём место (если его вместимость больше текущего кол-ва других птичек)
        return self.is_active and self.current_birds < self.perch_capacity

    def add_bird_to_perch(self): # Добавляем птицу на жердочку
        # тут значение либо True либо False (проверка на свободность жердочки)
        if self.is_perch_available(): # если жердочка доступна
            self.current_birds += 1 # увеличиваем количество сидящих на ней птиц на 1
            if self.current_birds >= self.perch_capacity:
                self.is_active = False # если слишком много птиц, столб пропадает
                self.recovery_timer = 50 # время восстановления жердочки 50 тиков (где-то +- 1.5 сек)

    def remove_bird_from_perch(self): # убираем птицу с жердочки
        self.current_birds = max(0, self.current_birds - 1)

    def update(self):
        if not self.is_active: # Если столб неактивен, уменьшаем таймер восстановления
            self.recovery_timer -= 1
            if self.recovery_timer <= 0: # столб восстанавливается, когда время восстановления истекает
                self.is_active = True # столб восстановлен
                self.current_birds = 0 # сбрасываем количество птиц на столбе (пустой новый столб)


# ОКНО
class BirdWindow(QMainWindow): # оформление окна
    def __init__(self, config):
        super().__init__()
        self.setWindowTitle('Birds')
        self.setGeometry(100, 100, 800, 400)

        # таймер для обновления состояния
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_state)
        self.timer.start(30) # обновляем каждые 30 миллисекунд

        # инициализация столбов из конфигурации
        post_config = config['posts']
        self.posts = [
            LampPost(post_config['start_x'] + i * post_config['x_spacing'],
                     post_config['start_y'],
                     random.randint(post_config['min_height'], post_config['max_height']))
            for i in range(post_config['count'])
        ]

        # инициализация птиц из конфигурации
        bird_config = config['birds']
        self.birds = [
            Bird(random.randint(bird_config['min_start_x'], bird_config['max_start_x']),
                 random.randint(bird_config['min_start_y'], bird_config['max_start_y']),
                 random.randint(bird_config['min_sit_time'], bird_config['max_sit_time']))
            for _ in range(bird_config['count'])
        ]

    def update_state(self):
        # для каждой птицы обновляем ее состояние
        for bird in self.birds:
            bird.update(self.posts)

        # для каждого столба обновляем его состояние
        for post in self.posts:
            post.update()

        # каждый раз перерисовываем окно
        self.repaint()

    def paintEvent(self, event): # рисовательная часть
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # фон
        painter.fillRect(self.rect(), QColor(220, 220, 220))

        # СТОЛБЫ
        for post in self.posts:
            if post.is_active:

                # столб
                painter.setPen(QPen(Qt.gray, 4))
                painter.drawLine(post.x, post.y, post.x, post.y - post.height)

                # жердочка
                painter.setPen(QPen(Qt.gray, 6))
                painter.drawLine(post.x - 15, post.y - post.height, post.x + 15, post.y - post.height)

        # ПТИЦЫ (кружочки)
        for bird in self.birds:
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(QBrush(Qt.green))
            painter.drawEllipse(bird.x - 10, bird.y - 10, 20, 20)


if __name__ == "__main__":
    config = load_config('config.json') # загружаем json файл
    app = QApplication(sys.argv) # создаем приложение с учетом характеристик устройства sys.argv
    window = BirdWindow(config)
    window.show()
    sys.exit(app.exec_()) # обеспечиваем корректность работы программы
