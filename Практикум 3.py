import sys
import random
import json
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QSpinBox, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen

# функция для загрузки конфигурации из JSON-файла
def load_config(filename):
    with open(filename, 'r') as file:
        config = json.load(file)  # загружаем конфигурацию как словарь
    return config



# КЛАСС ПТИЧЕК
class Bird:
    def __init__(self, start_x, start_y, sit_time):
        self.x = start_x # х стартовой позиции
        self.y = start_y # у стартовой позиции
        self.sit_time = sit_time # время, сколько птица сидит на столбе
        self.target_post = None # целевой столб, куда птица хочет сесть
        self.sitting_time = 0 # текущее время, которое она сидит
        self.is_flying_away = False # состояние "улетает ли птица"
        self.is_hopping = False # состояние "пересаживается ли птица"
        self.angle = 0
        self.horizontal_speed = 0 # скорость перелета по горизонтали
        self.vertical_speed = 3 # скорость улетания
        self.hop_start = (0, 0)  # начальная точка перелета
        self.hop_end = (0, 0)  # конечная точка перелета
        self.hop_t = 0  # параметр времени для перелёта по дуге

    def move_to(self, post_x, perch_y): # птица летит к целевой жердочке
        self.x += (post_x - self.x) * 0.05
        self.y += (perch_y - self.y) * 0.05

    def start_fly_away(self): # для того чтобы птички улетали вверх
        # случайный угол для полета в радианах
        self.angle = math.radians(random.choice(range(20, 160)))
        self.horizontal_speed = math.cos(self.angle) * self.vertical_speed

    def fly_away(self):
        # обновление положение птицы
        self.x += self.horizontal_speed
        self.y -= self.vertical_speed

        # синусоида
        self.x += math.sin(self.y * 0.1) * 2

    def hop_to(self, target_post): # для перелета по дуге к новому столбу
        self.is_hopping = True
        self.hop_start = (self.x, self.y)
        self.hop_end = (target_post.x, target_post.y - target_post.height)
        self.hop_t = 0  # начало перелёта по времени
        self.target_post = target_post

    def fly_arc(self): # перелет по дуге между столбами
        if self.hop_t <= 1:
            start_x, start_y = self.hop_start
            end_x, end_y = self.hop_end

            # парабола
            self.x = (1 - self.hop_t) * start_x + self.hop_t * end_x
            self.y = (1 - self.hop_t) * start_y + self.hop_t * end_y - math.sin(math.pi * self.hop_t) * 50

            self.hop_t += 0.02  # увеличиваем время полета
        else:
            # прекращение полета и сброс времени полета
            self.is_hopping = False
            self.hop_t = 0


    def update(self, posts):  # изменение состояния птички

        if self.is_hopping:
            # если птица перелетает по параболе
            self.fly_arc()
            if not self.is_hopping:
                # когда птичка прилетает
                if self.target_post:
                    self.target_post.add_bird_to_perch()
                self.sitting_time = 0

        elif not self.is_flying_away: # если птичка не улетает
            # если текущий столб упал или птица не выбрала столб, она выбирает новый/другой доступный столб
            if self.target_post is None or not self.target_post.is_active: # если столб упал или неактивен
                # пересаживается на любой доступный столб, кроме того,с которого улетала
                available_posts = [post for post in posts if post.is_perch_available() and post != self.target_post]
                if available_posts:
                    self.target_post = random.choice(available_posts)

            if self.target_post and self.target_post.is_perch_available(): # eсли птица выбрала посидеть на столбe

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
                        if self.target_post:
                            self.target_post.remove_bird_from_perch() # убираем птичку со столба

                        # вероятность 50%: либо улетает, либо пересаживается на другой столб
                        if random.random() < 0.5:
                            self.is_flying_away = True
                            self.start_fly_away()
                        else:
                            # птичка пересаживается на другой столб
                            available_posts = [post for post in posts if post.is_perch_available() and post != self.target_post]
                            if available_posts:
                                new_target_post = random.choice(available_posts)
                                self.hop_to(new_target_post)

        else:
            self.fly_away() # птица улетает вверх
            self.target_post.remove_bird_from_perch()

            # когда птица вылетает за пределы окна, она возвращается в случайное место сверху (обновление птичек)
            if self.y < -50 or self.x < -50 or self.x > 850:
                if self.target_post:
                    self.target_post.remove_bird_from_perch()  # убираем с текущего столба
                self.is_flying_away = False
                self.target_post = None
                self.sitting_time = 0
                self.y = random.randint(-100, -50)
                self.x = random.randint(50, 750)




# КЛАСС СТОЛБОВ
class LampPost:
    def __init__(self, x, y, height, perch_capacity=5): # максимум 5 птичек на одном столбе, иначе он падает
        self.x = x
        self.y = y
        self.height = height  # высота столба
        self.perch_capacity = perch_capacity  # максимальное количество птиц на жердочке
        self.current_birds = 0  # текущее количество птиц на жердочке
        self.is_active = True  # состояние столба (активен или нет)
        self.recovery_timer = 0  # таймер для восстановления столба
        self.default_recovery_time = 50  # время восстановления столба по умолчанию

    def is_perch_available(self): # птичка садится только на существующую жердочку, на которой есть место
        # проверяем, активен ли столб и есть ли на нём место (если его вместимость больше текущего кол-ва других птичек)
        return self.is_active and self.current_birds < self.perch_capacity

    def add_bird_to_perch(self): # Добавляем птицу на жердочку
        # тут значение либо True либо False (проверка на свободность жердочки)
        if self.is_perch_available(): # если жердочка доступна
            self.current_birds += 1 # увеличиваем количество сидящих на ней птиц на 1
            if self.current_birds >= self.perch_capacity:
                self.is_active = False # если слишком много птиц, столб пропадает
                self.recovery_timer = self.default_recovery_time # время восстановления жердочки 50 тиков (где-то +- 1.5 сек)

    def remove_bird_from_perch(self): # убираем птицу с жердочки
        self.current_birds = max(0, self.current_birds - 1)

    def update(self):
        if not self.is_active: # Если столб неактивен, уменьшаем таймер восстановления
            self.recovery_timer -= 1
            if self.recovery_timer <= 0: # столб восстанавливается, когда время восстановления истекает
                self.is_active = True  # столб восстановлен
                self.current_birds = 0 # сбрасываем количество птиц на столбе (пустой новый столб)

    def set_recovery_time(self, time): # возможность установить новое время восстановления столба
        self.default_recovery_time = time

    def set_perch_capacity(self, capacity):
        self.perch_capacity = capacity


# ОКНО
class BirdWindow(QMainWindow): # оформление окна
    def __init__(self, config):
        super().__init__()
        self.setWindowTitle('Birds')
        self.setGeometry(100, 100, 800, 500)

        # таймер для обновления состояния
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_state)
        self.timer.start(20) # обновляем каждые 20 миллисекунд

        # инициализация столбов из конфигурации
        post_config = config['posts']
        self.posts = []
        self.post_spinboxes = []

        for i in range(post_config['count']):
            self.add_post(
                post_config['start_x'] + i * post_config['x_spacing'],
                post_config['start_y'],
                random.randint(post_config['min_height'], post_config['max_height'])
            )

        # инициализация птиц из конфигурации
        bird_config = config['birds']
        self.birds = [
            Bird(random.randint(bird_config['min_start_x'], bird_config['max_start_x']),
                 random.randint(bird_config['min_start_y'], bird_config['max_start_y']),
                 random.randint(bird_config['min_sit_time'], bird_config['max_sit_time']))
            for _ in range(bird_config['count'])
        ]

        # элементы управления Spinbox
        self.bird_count_spinbox = QSpinBox(self) # SpinBox для изменения количества птиц
        self.bird_count_spinbox.setRange(1, 50) # пределы изменения количества птичек
        self.bird_count_spinbox.setValue(len(self.birds)) # устанавливаем нач значение кол-ва птичек

        # вызываем метод update_bird_count при каждом изменении значения кол-ва птиц в спинбоксе
        self.bird_count_spinbox.valueChanged.connect(self.update_bird_count)

        self.recovery_time_spinbox = QSpinBox(self) # SpinBox для изменения времени восстановления столбов
        self.recovery_time_spinbox.setRange(10, 200) # пределы изменения времени восстановления столбов
        self.recovery_time_spinbox.setValue(50) # нач значение времени восстановления

        # вызываем метод update_recovery_time при каждом изменении значения времени восстановления столбов
        self.recovery_time_spinbox.valueChanged.connect(self.update_recovery_time)

        # 10, 10 — это координаты верхнего левого угла виджета SpinBox относительно окна приложения
        self.bird_count_spinbox.move(10, 10)
        self.recovery_time_spinbox.move(10, 40)

    def add_post(self, x, y, height):  # добавление начального столба
        post = LampPost(x, y, height)
        self.posts.append(post)

        spinbox = QSpinBox(self)
        spinbox.setGeometry(x - 20, y + 20, 30, 20)  # настройка размеров спинбокса для вместимости столба
        spinbox.setRange(1, 20)
        spinbox.setValue(post.perch_capacity)
        spinbox.move(x - 20, y + 20)
        spinbox.valueChanged.connect(lambda value, p=post: p.set_perch_capacity(value))  # Устанавливаем связь
        spinbox.show()

        self.post_spinboxes.append(spinbox)

    def update_bird_count(self, count): # добавляет или удаляет птиц, чтобы их количество соответствовало новому значению в SpinBox
        # инициализация птиц из конфигурации
        bird_config = config['birds']
        current_count = len(self.birds)

        if count > current_count:
            # добавляем новых птиц
            for i in range(count - current_count):
                new_bird = Bird(
                    random.randint(bird_config['min_start_x'], bird_config['max_start_x']),
                    random.randint(bird_config['min_start_y'], bird_config['max_start_y']),
                    random.randint(bird_config['min_sit_time'], bird_config['max_sit_time'])
                )
                self.birds.append(new_bird)
        elif count < current_count:
            # удаляем лишних птиц
            self.birds = self.birds[:count]

    def update_recovery_time(self, time):
        # обновляем время восстановления столбов
        for post in self.posts:
            post.set_recovery_time(time)

    def mousePressEvent(self, event): # добавление нового столба по клику
        x, y = event.x(), event.y()  # возвращает координату x курсора мыши относительно левого верхнего угла виджета (во время клика)
        self.add_post(x, 300, random.randint(100, 200)) # новый столб появляется на том же уровне, что и основные столбы

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
        # Рисуем окно
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
            painter.drawEllipse(int(bird.x) - 10, int(bird.y) - 10, 20, 20)

if __name__ == "__main__":
    config = load_config('config.json') # загружаем json файл
    app = QApplication(sys.argv) # создаем приложение с учетом характеристик устройства sys.argv
    window = BirdWindow(config)
    window.show()
    sys.exit(app.exec_()) # обеспечиваем корректность работы программы
