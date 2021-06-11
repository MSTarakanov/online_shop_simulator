from common import json
from common import role
from common import show_menu


# Функции, для регистрации пользователя
def write_to_users_json(newName, newLogin, newPassword):
    with open('users.json', 'r', encoding='UTF-8') as users_r:
        file = json.load(users_r)
    with open('users.json', 'w', encoding='UTF-8') as users_w:
        user_info = {'name': newName, 'login': newLogin, 'password': newPassword, 'role': role.GUEST}
        file.append(user_info)
        json.dump(file, users_w, indent=2, ensure_ascii=False)


def registration():
    newName = input("Введите свое имя: ")
    newLogin = input("Введите свой логин: ")
    newPassword = input("Введите свой пароль: ")
    newPasswordConfirm = input("Подтвердите пароль: ")
    while newPassword != newPasswordConfirm:
        newPassword = input("Введите свой пароль еще раз: ")
        newPasswordConfirm = input("Подтвердите пароль: ")
    write_to_users_json(newName, newLogin, newPassword)
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'])


ClientMenuFunctions = { 'Регистрация': registration,
                        'Каталог': view_catalog,
                        'Авторизация': authorize,
                        'Выйти из аккаунта': logout,
                        'Заказы': view_orders,
                        'Выйти': exit}


def main():
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'])


main()
