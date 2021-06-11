# подключим нужные библиотеки
import os
import msvcrt


class OrderStatus:
    CREATED = 'Создан'
    PAID = 'Оплачен'
    SENT = 'Отправлен'
    DELIVERED = 'Доставлен'


class Button:
    UP = 72
    DOWN = 80
    RIGHT = 77
    LEFT = 75
    ENTER = 13
    q = 113


class Role:
    ADMIN = 'admin'
    GUEST = 'guest'


status = OrderStatus()
button = Button()
role = Role()
currentUser = {}


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


def get_max_id(orders):
    max_id = 0
    for order in orders:
        if order['id'] > max_id:
            max_id = order['id']
    return max_id


def get_order_products_amount(order):
    order_products_amount = 0
    for values in order['products'].values():
        order_products_amount += values['amount']
    return order_products_amount


def get_order_sum(order):
    order_sum = 0
    for values in order['products'].values():
        order_sum += values['amount'] * values['price']
    return order_sum


def get_status(menuFunctions):
    return show_menu([status.PAID, status.SENT, status.DELIVERED], menuFunctions)


def get_order_index(find_to_order, user_order_list):
    for order in user_order_list:
        if order['id'] == find_to_order['id']:
            return order


# функции меню
def update_menu(listOfPoints, currentPoint):
    os.system("cls")
    for point in enumerate(listOfPoints):
        if point[0] + 1 == currentPoint:
            print(f"* {point[1]}")
        else:
            print(f"  {point[1]}")


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
