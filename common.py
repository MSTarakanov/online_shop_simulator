# подключим нужные библиотеки
import json
import os
import msvcrt
import cursor
import datetime as dt

# подключим функции
from client import *

currentUser = {}


def update_admin_catalog(catalog, currentRow, currentColumn):
    os.system("cls")
    print(f'Приветствуем, администратор {currentUser["name"]}')
    print('Для управления каталогом используются стрелки клавиатуры, для изменения нажмите Enter')
    print('Для выхода из каталога нажмите "q"')
    for product, values in catalog['products'].items():
        print('%-15s' % product, end='')
        if currentColumn == 1 and currentRow == product:
            print('\033[31mЦена: %-4d\033[0m' % (values['price']), end='')
        else:
            print('Цена: %-4d' % (values['price']), end='')
        if currentColumn == 2 and currentRow == product:
            print('\033[31mКоличество: %d\033[0m' % (values['amount']))
        else:
            print('Количество: %d' % (values['amount']))


def update_guest_catalog(catalog, currentRow, currentColumn):
    os.system("cls")
    print(f'Приветствуем, {currentUser["name"]}')
    print('Для управления каталогом используются стрелки клавиатуры')
    print('Для выхода из каталога нажмите "q"')
    print('%66s' % 'Количество в корзине')
    for product, values in catalog['products'].items():
        print('%-15s Цена: %-4d  Количество на складе: %-4d' % (product, values['price'], values['amount']), end='')
        if currentRow == product:
            if currentColumn != get_cart_product_amount(product):
                change_cart_product_value(product, currentColumn, catalog['products'][product]['price'])
            if catalog['products'][product]['amount'] < get_cart_product_amount(product):
                print(f'\033[32m<\033[0m \033[31m{get_cart_product_amount(product)}\033[0m \033[32m>\033[0m')
            else:
                print(f'\033[32m<\033[0m {get_cart_product_amount(product)} \033[32m>\033[0m')
        else:
            if catalog['products'][product]['amount'] < get_cart_product_amount(product):
                print(f'  \033[31m{get_cart_product_amount(product)}\033[0m  ')
            else:
                print(f'  {get_cart_product_amount(product)}  ')
    if is_amount_error(catalog):
        print('Количество товаров на складе изменилось, некоторые товары больше недоступны')
        print('Уменьшите количество товаров в корзине до допустимого предела!')
    else:
        if currentRow != 'ok_btn':
            print('Сумма заказа: %-5d            Подтвердить и оплатить' % cart_sum())
        else:
            print('Сумма заказа: %-5d            \033[32mПодтвердить и оплатить\033[0m' % cart_sum())

def is_amount_error(catalog):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    if is_cart_exist(orders):
        cart = get_cart(orders)
        if any(catalog['products'][product]['amount'] < get_cart_product_amount(product) for product in
               cart.keys()):
            return True
    return False


def get_value():
    while True:
        newValue = input('Введите новое значение: ')
        try:
            newValue = int(newValue)
            break
        except ValueError:
            print("That's not an int!")
    return newValue


def update_cart_prices(product_to_update, newPrice):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    for order in orders['orders']:
        if order['status'] == 1:
            for product, values in order['products'].items():
                if product == product_to_update:
                    values['price'] = newPrice
    with open('orders.json', 'w', encoding='UTF-8') as orders_w:
        json.dump(orders, orders_w, indent=2, ensure_ascii=False)


def change_catalog_value(catalog, currentRow, currentColumn):
    newValue = get_value()
    if currentColumn == 1:
        catalog['products'][currentRow]['price'] = newValue
        update_cart_prices(currentRow, newValue)
    elif currentColumn == 2:
        catalog['products'][currentRow]['amount'] = newValue
    with open('catalog.json', 'w', encoding='UTF-8') as catalog_w:
        json.dump(catalog, catalog_w, indent=2, ensure_ascii=False)
    return catalog


def show_login_catalog(catalog):
    currentRow = list(catalog['products'].keys())[0]
    if currentUser['role'] == 'admin':
        currentColumn = 1
    elif currentUser['role'] == 'guest':
        currentColumn = get_cart_product_amount(currentRow)
    pressedKey = None
    if currentUser['role'] == 'admin':
        update_admin_catalog(catalog, currentRow, currentColumn)
    elif currentUser['role'] == 'guest':
        update_guest_catalog(catalog, currentRow, currentColumn)
    while pressedKey != 113:  # q
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            # down
            if pressedKey == 80 and currentRow != 'ok_btn':
                if (list(catalog['products'].keys()).index(currentRow) < len(catalog['products']) - 1 and currentUser['role'] == 'admin') or \
                   (list(catalog['products'].keys()).index(currentRow) < len(catalog['products']) and currentUser['role'] == 'guest'):
                    try:
                        currentRow = list(catalog['products'].keys())[list(catalog['products'].keys()).index(currentRow) + 1]
                    except:
                        currentRow = 'ok_btn'
                    if currentUser['role'] == 'guest':
                        currentColumn = get_cart_product_amount(currentRow)
            # up
            elif pressedKey == 72 and currentRow != 'ok_btn' and list(catalog['products'].keys()).index(currentRow) > 0:
                currentRow = list(catalog['products'].keys())[list(catalog['products'].keys()).index(currentRow) - 1]
                if currentUser['role'] == 'guest':
                    currentColumn = get_cart_product_amount(currentRow)
            elif pressedKey == 72 and currentRow == 'ok_btn':
                currentRow = list(catalog['products'].keys())[-1]
            # right
            elif pressedKey == 77 and currentRow != 'ok_btn' and ((currentUser['role'] == 'admin' and currentColumn < 2) or
                 currentUser['role'] == 'guest' and currentColumn < catalog['products'][currentRow]['amount']):
                currentColumn += 1
            # left
            elif pressedKey == 75 and currentRow != 'ok_btn' and ((currentUser['role'] == 'admin' and currentColumn > 1) or
                                       (currentUser['role'] == 'guest' and currentColumn > 0)):
                currentColumn -= 1
            # enter
            elif pressedKey == 13:
                if currentUser['role'] == 'admin':
                    catalog = change_catalog_value(catalog, currentRow, currentColumn)
                elif currentUser['role'] == 'guest' and currentRow == 'ok_btn':
                    accept_order()
            if currentUser['role'] == 'admin':
                update_admin_catalog(catalog, currentRow, currentColumn)
            elif currentUser['role'] == 'guest':
                update_guest_catalog(catalog, currentRow, currentColumn)
    if currentUser['role'] == 'admin':
        show_menu(['Каталог', 'Заказы', 'Выйти из аккаунта'])
    elif currentUser['role'] == 'guest':
        show_menu(['Каталог', 'Корзина', 'Заказы', 'Выйти из аккаунта'])


def accept_order():
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    for order in orders['orders']:
        if order['status'] == 1:
            order['status'] = 2
    with open('orders.json', 'w', encoding='UTF-8') as orders_w:
        json.dump(orders, orders_w, indent=2, ensure_ascii=False)


def show_catalog(catalog):
    print('Для возможности взаимодействия с каталогом авторизуйтесь')
    print('Для выхода из каталога нажмите любую клавишу')
    for product, values in catalog['products'].items():
        print('%-15s Цена: %-4d Количество: %d' % (product, values['price'], values['amount']))
    while not msvcrt.getch():
        pass
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'])


def get_max_id(orders):
    max_id = 0
    for order in orders['orders']:
        if order['id'] > max_id:
            max_id = order['id']
    return max_id

def is_cart_exist(orders):
    if any(order['user'] == currentUser['login'] and order['status'] == 1 for order in orders['orders']):
        return True
    return False

def change_cart_product_value(productName, newProductAmount, productPrice):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    if not is_cart_exist(orders) and newProductAmount != 0:
        orders['orders'].append({"id": get_max_id(orders) + 1, "user": currentUser['login'],
                                 "date": dt.datetime.now().strftime('%d.%m.%y %H:%M'), "status": 1, "products": {}})
    for order in orders['orders']:
        if order['user'] == currentUser['login'] and order['status'] == 1:
            if productName not in order['products']:
                order['products'][productName] = {'price': productPrice, 'amount': newProductAmount}
            for product, values in order['products'].items():
                if product == productName and newProductAmount != 0:
                    values['amount'] = newProductAmount
                elif product == productName and newProductAmount == 0:
                    order['products'].pop(product)
                    if order['products'] == {}:
                        orders['orders'].remove(order)
                    break
    with open('orders.json', 'w', encoding='UTF-8') as orders_w:
        json.dump(orders, orders_w, indent=2, ensure_ascii=False)


def get_cart(orders):
    for order in orders['orders']:
        if order['user'] == currentUser['login'] and order['status'] == 1:
            return order['products']
    return None


def get_cart_product_amount(product_name):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    cart = get_cart(orders)
    if cart:
        for product, values in cart.items():
            if product == product_name:
                return values['amount']
    return 0


def view_catalog():
    with open('catalog.json', 'r', encoding='UTF-8') as catalog_r:
        catalog = json.load(catalog_r)
    if currentUser == {}:
        show_catalog(catalog)
    elif currentUser['role'] == 'guest' or currentUser['role'] == 'admin':
        show_login_catalog(catalog)


def authorize():
    with open('users.json', 'r', encoding='UTF-8') as users_r:
        usersFile = json.load(users_r)
    allLogins = list(map(lambda x: x['login'], usersFile['users']))
    login = input("Введите логин: ")
    while not allLogins.__contains__(login):
        print('Пользователь не найден')
        login = input("Введите логин: ")
    password = input("Введите пароль: ")
    for user in usersFile['users']:
        if user['login'] == login:
            correctPassword = user['password']
            while password != correctPassword:
                print('Неправильный пароль')
                password = input("Введите пароль: ")
            global currentUser
            currentUser = user
    if currentUser['role'] == 'guest':
        show_menu(['Каталог', 'Корзина', 'Заказы', 'Выйти из аккаунта'])
    elif currentUser['role'] == 'admin':
        show_menu(['Каталог', 'Заказы', 'Выйти из аккаунта'])


def logout():
    global currentUser
    currentUser = {}
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'])


def cart_sum():
    sum = 0
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    if is_cart_exist(orders):
        cart = get_cart(orders)
        for values in cart.values():
            sum += values['price'] * values['amount']
    return sum


# def update_cart():
#     with open('orders.json', 'r', encoding='UTF-8') as orders_r:
#         orders = json.load(orders_r)
#     if is_cart_exist(orders):
#         cart = get_cart(orders)
#         for product, values in cart.items():
#             print('%-15s Цена: %-4d Количество: %d' % (product, values['price'], values['amount']))
#         print('Сумма заказа: %-5d Подтвердить и оплатить' % cart_sum(cart))
#     else:
#         print('Ваша корзина пуста! Добавьте товары через каталог')
#
#
#
# def show_cart():
#     update_cart()




menuFunctions = {'Регистрация': registration,
                 'Каталог': view_catalog,
                 'Авторизация': authorize,
                 'Выйти из аккаунта': logout,
                 # 'Корзина': show_cart,
                 'Выйти': exit}


# функции меню
def update_menu(listOfPoints, currentPoint):
    os.system("cls")
    for point in enumerate(listOfPoints):
        if point[0] + 1 == currentPoint:
            print(f"* {point[1]}")
        else:
            print(f"  {point[1]}")


def show_menu(listOfPoints):
    pressedKey = None
    currentPoint = 1
    update_menu(listOfPoints, currentPoint)
    while pressedKey != 113 and pressedKey != 13:  # q
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            # down
            if pressedKey == 80 and currentPoint < len(listOfPoints):
                currentPoint += 1
                update_menu(listOfPoints, currentPoint)
            # up
            if pressedKey == 72 and currentPoint > 1:
                currentPoint -= 1
                update_menu(listOfPoints, currentPoint)
            # enter
            if pressedKey == 13:
                os.system("cls")
                menuFunctions[listOfPoints[currentPoint - 1]]()


# основная функция
def main():
    cursor.hide()
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'])
    # with open('orders.json', 'r', encoding='UTF-8') as orders_r:
    #     orders = json.load(orders_r)
    # if True in (order['user'] == 'Max' and order['status'] == 3 for order in orders['orders']):
    #     print(orders['orders'])
    cursor.show()


main()
