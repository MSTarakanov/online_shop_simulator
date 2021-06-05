# подключим нужные библиотеки
import json
import os
import msvcrt
import cursor


# подключим функции
from client import *

currentUser = {}


def out_red_text(text):
    print("\033[31m{}\033[0m".format(text))


def update_admin_catalog(catalog, currentRow, currentColumn):
    os.system("cls")
    print(f'Приветствуем, администратор {currentUser["name"]}')
    print('Для управления каталогом используются стрелки клавиатуры, для изменения нажмите Enter')
    print('Для выхода из каталога нажмите "q"')
    for product in enumerate(catalog['products']):
        print('%-15s' % (product[1]['product_name']), end='')
        if currentColumn == 1 and currentRow == product[0] + 1:
            print('\033[31mЦена: %-4d\033[0m' % (product[1]['price']), end='')
        else:
            print('Цена: %-4d' % (product[1]['price']), end='')
        if currentColumn == 2 and currentRow == product[0] + 1:
            print('\033[31mКоличество: %d\033[0m' % (product[1]['amount']))
        else:
            print('Количество: %d' % (product[1]['amount']))


def get_value():
    while True:
        newValue = input('Введите новое значение: ')
        try:
            newValue = int(newValue)
            break
        except ValueError:
            print("That's not an int!")
    return newValue


def update_catalog(catalog, currentRow, currentColumn):
    newValue = get_value()
    currentRow -= 1
    if currentColumn == 1:
        catalog['products'][currentRow]['price'] = newValue
    elif currentColumn == 2:
        catalog['products'][currentRow]['amount'] = newValue
    with open('catalog.json', 'w', encoding='UTF-8') as catalog_w:
        json.dump(catalog, catalog_w, indent=2, ensure_ascii=False)
    with open('catalog.json', 'r', encoding='UTF-8') as catalog_r:
        newCatalog = json.load(catalog_r)
    return newCatalog


def show_admin_catalog(catalog):
    currentRow = 1
    currentColumn = 1
    pressedKey = None
    update_admin_catalog(catalog, currentRow, currentColumn)
    while pressedKey != 113:  # q
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            # down
            if pressedKey == 80 and currentRow < len(catalog['products']):
                currentRow += 1
            # up
            elif pressedKey == 72 and currentRow > 1:
                currentRow -= 1
            # right
            elif pressedKey == 77 and currentColumn < 2:
                currentColumn += 1
            # left
            elif pressedKey == 75 and currentColumn > 1:
                currentColumn -= 1
            # enter
            elif pressedKey == 13:
                catalog = update_catalog(catalog, currentRow, currentColumn)
            update_admin_catalog(catalog, currentRow, currentColumn)
    show_menu(['Каталог', 'Заказы', 'Выйти из аккаунта'])


def show_catalog(catalog):
    print('Для возможности взаимодействия с каталогом авторизуйтесь')
    print('Для выхода из каталога нажмите любую клавишу')
    pressedKey = None
    for product in catalog['products']:
        print('%-15s Цена: %-4d Количество: %d' % (product['product_name'], product['price'], product['amount']))
    while not msvcrt.getch():
        pass
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'])


def update_guest_catalog(catalog, currentProduct):
    os.system("cls")
    print(f'Приветствуем, {currentUser["name"]}')
    for product in enumerate(catalog['products']):
        print('%-15s Price: %-4d Количество: %-4d' % (product[1]['product_name'], product[1]['price'], product[1]['amount']), end='')
        if currentProduct == product[0] + 1:
            print('< 0 >')
        else:
            print('  0  ')


def show_guest_catalog(catalog):
    currentRow = 1
    pressedKey = None
    update_guest_catalog(catalog, currentRow)
    while pressedKey != 113:  # q
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            # down
            if pressedKey == 80 and currentRow < len(catalog['products']):
                currentRow += 1
            # up
            elif pressedKey == 72 and currentRow > 1:
                currentRow -= 1
            # # right
            # elif pressedKey == 77 and currentColumn < 2:
            #     currentColumn += 1
            # # left
            # elif pressedKey == 75 and currentColumn > 1:
            #     currentColumn -= 1
            update_guest_catalog(catalog, currentRow)


def view_catalog():
    with open('catalog.json', 'r', encoding='UTF-8') as catalog_r:
        catalog = json.load(catalog_r)
    if currentUser == {}:
        show_catalog(catalog)
    elif currentUser['role'] == 'guest':
        show_guest_catalog(catalog)
    elif currentUser['role'] == 'admin':
        show_admin_catalog(catalog)


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


menuFunctions = {'Регистрация': registration,
                 'Каталог': view_catalog,
                 'Авторизация': authorize,
                 'Выйти из аккаунта': logout,
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


main()
