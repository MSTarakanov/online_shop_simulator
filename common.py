# подключение нужных библиотек
import os
import msvcrt


# класс-перечисление статусов заказа
class OrderStatus:
    CREATED = 'Создан'
    PAID = 'Оплачен'
    SENT = 'Отправлен'
    DELIVERED = 'Доставлен'


# класс-перечисление численного значения кнопок
class Button:
    UP = 72     # стрелка вверх
    DOWN = 80   # стрелка вниз
    RIGHT = 77  # стрелка вправо
    LEFT = 75   # стрелка влево
    ENTER = 13  # клавиша Enter
    q = 113     # клавиша q


# инициализация классов-перечеслений
status = OrderStatus()
button = Button()


# функция для получения неотрицтельного целого значения от пользователя
def get_value():
    while True:
        newValue = input('Введите новое значение: ')
        try:
            newValue = int(newValue)
            assert (newValue >= 0)
            break
        except ValueError:
            print("Введите целое число!")
        except AssertionError:
            print("Введите положительное число!")
    return newValue


# функция для вычисления следующего уникального id для номера заказа
def get_max_id(orders):
    max_id = 0
    for order in orders:
        if order['id'] > max_id:
            max_id = order['id']
    return max_id


# функция, которая возвращает количество продуктов в заказе
def get_order_products_amount(order):
    order_products_amount = 0
    for values in order['products'].values():
        order_products_amount += values['amount']
    return order_products_amount


# функция, возвращающая сумму заказа
def get_order_sum(order):
    order_sum = 0
    for values in order['products'].values():
        order_sum += values['amount'] * values['price']
    return order_sum


# функция, возвращающая статус, который выбрал пользлватель в меню
def get_status(menuFunctions):
    return show_menu([status.PAID, status.SENT, status.DELIVERED], menuFunctions)


# функция, возвращающая индекс заказа в списке заказов
def get_order_index(find_to_order, user_order_list):
    for order in user_order_list:
        if order['id'] == find_to_order['id']:
            return order


# ФУНКЦИИ МЕНЮ
# обновление вида меню с учетом текущей позиции "курсора"
def update_menu(listOfPoints, currentPoint):
    os.system("cls")
    for point in enumerate(listOfPoints):
        if point[0] + 1 == currentPoint:
            print(f"* {point[1]}")
        else:
            print(f"  {point[1]}")


# реакиция меню на действия пользователя (изменение значения положения курсора/нажатие на Enter)
def show_menu(listOfPoints, menuFunctions):
    pressedKey = None
    currentPoint = 1
    update_menu(listOfPoints, currentPoint)
    while pressedKey != button.q and pressedKey != button.ENTER:
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            # down
            if pressedKey == button.DOWN and currentPoint < len(listOfPoints):
                currentPoint += 1
                update_menu(listOfPoints, currentPoint)
            # up
            if pressedKey == button.UP and currentPoint > 1:
                currentPoint -= 1
                update_menu(listOfPoints, currentPoint)
            # enter
            if pressedKey == button.ENTER:
                os.system("cls")
                return menuFunctions[listOfPoints[currentPoint - 1]]()
