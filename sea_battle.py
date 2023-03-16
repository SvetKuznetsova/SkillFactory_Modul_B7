from random import randint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за границы доски"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Dot:  # Класс точек на поле
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):  # Метод для проверки принадлежности точки
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f"({self.x}, {self.y})"

class Ship:  # Класс корабля
    def __init__(self, bow, l, o):
        self.bow = bow  # точка размещения носа корабля
        self.l = l  # длина корабля
        self.o = o  # вертикальное или горизонтальное размещение корабля
        self.lives = l  # количество жизней корабля
    
    @property
    def dots(self):
        ship_dots = []  # список всех точек корабля
        for i in range(self.l):
            cur_x = self.bow.x 
            cur_y = self.bow.y
            
            if self.o == 0:  # горизонтальное размещение корабля
                cur_x += i
            
            elif self.o == 1:  # вертикальное размещение корабля
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def shooten(self, shot):
        return shot in self.dots

class Board:  # Игровая доска
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid  # параметр, указывающий, нужно ли скрывать корабли на доске
        
        self.count = 0  # количество пораженных кораблей
        
        self.field = [ ["O"]*size for _ in range(size) ]
        
        self.busy = []  # список занятых точек (корабли, совершенные выстрелы)
        self.ships = []  # список кораблей
    
    def add_ship(self, ship):  # постановка корабля на доску
        
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        
        self.ships.append(ship)
        self.contour(ship)
            
    def contour(self, ship, verb = False):  # установка точек контура корабля
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)
    
    def __str__(self):  # вывод доски
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        
        if self.hid:
            res = res.replace("■", "O")  # скрытие корабля на доске
        return res
    
    def out(self, d):  # проверка принадлежности координат точки доске
        return not((0<= d.x < self.size) and (0<= d.y < self.size))

    def shot(self, d):  # выполнение выстрела
        if self.out(d):  # проверка на попадание выстрела в пределы игрового поля
            raise BoardOutException()
        
        if d in self.busy:  # проверка на попадание выстрела в свободную точку
            raise BoardUsedException()
        
        self.busy.append(d)
        
        for ship in self.ships:  # проверка попадания выстрела в корабль
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:        # проверка наличия оставшихся жизней корабля
                    self.count += 1
                    self.contour(ship, verb = True)  # обведение корабля по контуру после уничтожения
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False
    
    def begin(self):
        self.busy = []

    def defeat(self):  # проверка на наличие неподбитых кораблей
        return self.count == len(self.ships)

class Player:        # Класс игрока
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError()
    
    def move(self):  # осуществление выстрела
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):  # Класс противника (компьютер)
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):  # Класс игрока
    def ask(self):
        while True:
            print("Введите координаты через пробел:")
            print("  - номер строки  ")
            print("  - номер столбца ")
            cords = input("Ваш ход: ").split()
            
            if len(cords) != 2:  # Проверка количества введенных координат
                print(" Необходимо ввести 2 координаты! ")
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1)

class Game:  # Класс Игра
    def __init__(self, size = 6):
        self.size = size
        self.lens = [3, 2, 2, 1, 1, 1, 1]  # количество и размер кораблей
        pl = self.random_board()  #
        co = self.random_board()
        co.hid = True
        
        self.ai = AI(co, pl)
        self.us = User(pl, co)
    
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board
    
    def try_board(self):  # установка кораблей на доску
        board = Board(size = self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:  #  ограничение количества попыток установки корабля
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def welcome(self):
        print("********************")
        print("  Добро пожаловать ")
        print("      в игру       ")
        print("   МОРСКОЙ БОЙ    ")
        print("********************")

    
    def print_board(self):
        print("-" * 20)
        print("Доска игрока:")
        print(self.us.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)

    def loop(self):  # установление очередности хода и проверка возможности продолжать игру
        num = 0
        while True:
            self.print_board()
            if num % 2 == 0:
                print("-"*20)
                print("Ходит игрок!")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            
            if self.ai.board.defeat():  # завершение игры, если не осталось целых кораблей у противника
                self.print_board()
                print("-"*20)
                print("Игрок выиграл!")
                break
            
            if self.us.board.defeat():  # завершение игры, если не осталось целых кораблей у игрока
                self.print_board()
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1
            
    def start(self):
        self.welcome()
        self.loop()
            
g = Game()
g.start()