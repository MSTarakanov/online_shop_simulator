import json


def write_to_users_json(newName, newLogin, newPassword):
    with open('users.json', 'r') as users_r:
        file = json.load(users_r)
    with open('users.json', 'w') as users_w:
        target = file['users']
        user_info = {'name': newName, 'login': newLogin, 'password': newPassword, 'role': 'guest'}
        target.append(user_info)
        json.dump(file, users_w, indent=2)


def registration():
    newName = input("Введите свое имя: ")
    newLogin = input("Введите свой логин: ")
    newPassword = input("Введите свой пароль: ")
    newPasswordConfirm = input("Подтвердите пароль: ")
    while newPassword != newPasswordConfirm:
        newPassword = input("Введите свой пароль еще раз: ")
        newPasswordConfirm = input("Подтвердите пароль: ")
    write_to_users_json(newName, newLogin, newPassword)
