# подключим нужные библиотеки
import os
import msvcrt


# подключим функции
from client import *


def view_catalog():
    with open('catalog.json', 'r') as catalog_r:
        catalog = json.load(catalog_r)
    for product in catalog['products']:
        print('%-15s Price: %-4d Amount: %d' % (product['product_name'], product['price'], product['amount']))


def authorize():
    with open('users.json', 'r') as users_r:
        usersFile = json.load(users_r)
    allLogins = list(map(lambda x: x['login'], usersFile['users']))
    login = input("Введите логин: ")
    while not allLogins.__contains__(login):
        print('User not found')
        login = input("Введите логин: ")
    password = input("Введите пароль: ")
    for user in usersFile['users']:
        if user['login'] == login:
            correctPassword = user['password']
            while password != correctPassword:
                print('Wrong password!')
                password = input("Введите пароль: ")
    print('success')


menuFunctions = {'Регистрация': registration, 'Каталог': view_catalog, 'Авторизация': authorize}


# функции меню
def update_menu(listOfPoints, current_point):
    os.system("cls")
    for point in enumerate(listOfPoints):
        if point[0] + 1 == current_point:
            print(f"* {point[1]}")
        else:
            print(f"  {point[1]}")


def show_menu(listOfPoints):
    pressedKey = None
    current_point = 1
    while pressedKey != 113 and pressedKey != 13:  # q
        update_menu(listOfPoints, current_point)
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            # print(pressedKey)
            # down
            if pressedKey == 80 and current_point < len(listOfPoints):
                current_point += 1
            # up
            if pressedKey == 72 and current_point > 1:
                current_point -= 1
            # enter
            if pressedKey == 13:
                os.system("cls")
                menuFunctions[listOfPoints[current_point - 1]]()


# основная функция
def main():
    show_menu(["Каталог", "Авторизация", "Регистрация"])


main()
