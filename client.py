import datetime as dt
import json
from common import os, msvcrt
from common import button, status
from common import show_menu, get_order_products_amount, get_order_sum, get_order_index, get_max_id


# ФУНЦИИ КАТАЛОГА ПОЛЬЗОВАТЕЛЯ
# функция, которая возвращает сумму заказа в корзине
def get_cart_sum():
    cart_sum = 0
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    if is_cart_exist(orders):
        cart = get_cart(orders)
        for values in cart.values():
            cart_sum += values['price'] * values['amount']
    return cart_sum


# функция, определяющая есть ли на складе нужное количество товара
def is_amount_error(catalog):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    if is_cart_exist(orders):
        cart = get_cart(orders)
        if any(catalog[product]['amount'] < get_cart_product_amount(product) for product in
               cart.keys()):
            return True
    return False


# функция, определяющая существует ли открытая корзина
def is_cart_exist(orders):
    if any(order['user'] == currentUser['login'] and order['status'] == status.CREATED for order in orders):
        return True
    return False


# функция, которая изменяет значение продуктов в корзине пользователя
def change_cart_product_value(productName, newProductAmount, productPrice):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    if not is_cart_exist(orders) and newProductAmount != 0:
        orders.append({"id": get_max_id(orders) + 1, "user": currentUser['login'],
                       "date": dt.datetime.now().strftime('%d.%m.%y %H:%M'), "status": status.CREATED, "products": {}})
    for order in orders:
        if order['user'] == currentUser['login'] and order['status'] == status.CREATED:
            if productName not in order['products']:
                order['products'][productName] = {'price': productPrice, 'amount': newProductAmount}
            for product, values in order['products'].items():
                if product == productName and newProductAmount != 0:
                    values['amount'] = newProductAmount
                elif product == productName and newProductAmount == 0:
                    order['products'].pop(product)
                    if order['products'] == {}:
                        orders.remove(order)
                    break
    with open('orders.json', 'w', encoding='UTF-8') as orders_w:
        json.dump(orders, orders_w, indent=2, ensure_ascii=False)


# функция, обновляющая вид каталога для пользователя
def update_guest_catalog(catalog, currentRow, currentColumn):
    os.system("cls")
    print(f'Приветствуем, {currentUser["name"]}')
    print('Для управления каталогом используются стрелки клавиатуры')
    print('Для выхода из каталога нажмите "q"')
    print('%66s' % 'Количество в корзине')
    for product, values in catalog.items():
        print('%-15s Цена: %-4d  Количество на складе: %-4d' % (product, values['price'], values['amount']), end='')
        if currentRow == product:
            if currentColumn != get_cart_product_amount(product):
                change_cart_product_value(product, currentColumn, catalog[product]['price'])
            if catalog[product]['amount'] < get_cart_product_amount(product):
                print(f'\033[32m<\033[0m \033[31m{get_cart_product_amount(product)}\033[0m \033[32m>\033[0m')
            else:
                print(f'\033[32m<\033[0m {get_cart_product_amount(product)} \033[32m>\033[0m')
        else:
            if catalog[product]['amount'] < get_cart_product_amount(product):
                print(f'  \033[31m{get_cart_product_amount(product)}\033[0m  ')
            else:
                print(f'  {get_cart_product_amount(product)}  ')
    if is_amount_error(catalog):
        print('Количество товаров на складе изменилось, некоторые товары больше недоступны')
        print('Уменьшите количество товаров в корзине до допустимого предела!')
    else:
        if get_cart_sum() != 0:
            if currentRow != 'ok_btn':
                print('Сумма заказа: %-5d            Подтвердить и оплатить' % get_cart_sum())
            else:
                print('Сумма заказа: %-5d            \033[32mПодтвердить и оплатить\033[0m' % get_cart_sum())


# функция, которая изменяет значение статуса после оплаты
def change_cart_status():
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    user_order = None
    for order in orders:
        if order['status'] == status.CREATED:
            order['status'] = status.PAID
            user_order = order
    with open('orders.json', 'w', encoding='UTF-8') as orders_w:
        json.dump(orders, orders_w, indent=2, ensure_ascii=False)
    return user_order


# функция, которая обновляет количество товара на складе после покупки пользователя
def update_products_amount(user_order, catalog):
    for product, values in user_order['products'].items():
        catalog[product]['amount'] -= values['amount']
    with open('catalog.json', 'w', encoding='UTF-8') as catalog_w:
        json.dump(catalog, catalog_w, indent=2, ensure_ascii=False)


# функция, позволяющая подтвердить и оплатить заказ
def accept_order(catalog):
    user_order = change_cart_status()
    update_products_amount(user_order, catalog)


# функция, которая реагирует на действия пользователя в каталоге
def show_login_catalog(catalog):
    currentRow = list(catalog.keys())[0]
    currentColumn = get_cart_product_amount(currentRow)
    pressedKey = None
    update_guest_catalog(catalog, currentRow, currentColumn)
    while pressedKey != button.q:  # q
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            # down
            if pressedKey == button.DOWN and currentRow != 'ok_btn':
                if list(catalog.keys()).index(currentRow) < len(catalog) - int(get_cart_sum() == 0):
                    try:
                        currentRow = list(catalog.keys())[list(catalog.keys()).index(currentRow) + 1]
                    except:
                        currentRow = 'ok_btn'
                    if currentRow != 'ok_btn':
                        currentColumn = get_cart_product_amount(currentRow)
            # up
            elif pressedKey == button.UP and currentRow != 'ok_btn' and list(catalog.keys()).index(currentRow) > 0:
                currentRow = list(catalog.keys())[list(catalog.keys()).index(currentRow) - 1]
                currentColumn = get_cart_product_amount(currentRow)
            elif pressedKey == button.UP and currentRow == 'ok_btn':
                currentRow = list(catalog.keys())[-1]
            # right
            elif pressedKey == button.RIGHT and currentRow != 'ok_btn' and \
                    currentColumn < catalog[currentRow]['amount']:
                currentColumn += 1
            # left
            elif pressedKey == button.LEFT and currentRow != 'ok_btn' and currentColumn > 0:
                currentColumn -= 1
            # enter
            elif pressedKey == button.ENTER and currentRow == 'ok_btn':
                accept_order(catalog)
                currentRow = list(catalog.keys())[-1]
                currentColumn = 0
            update_guest_catalog(catalog, currentRow, currentColumn)
    show_menu(['Каталог', 'Заказы', 'Выйти из аккаунта'], MenuFunctions)


# функция, которяа возвращает корзину пользователя
def get_cart(orders):
    for order in orders:
        if order['user'] == currentUser['login'] and order['status'] == status.CREATED:
            return order['products']
    return None


# функция, которая возвращает количество товара в корзине пользователя
def get_cart_product_amount(product_name):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    cart = get_cart(orders)
    if cart:
        for product, values in cart.items():
            if product == product_name:
                return values['amount']
    return 0


# функция, которая показывает каталог неваторизованному пользователю
def show_catalog(catalog):
    print('Для возможности взаимодействия с каталогом авторизуйтесь')
    print('Для выхода из каталога нажмите любую клавишу')
    for product, values in catalog.items():
        print('%-15s Цена: %-4d Количество: %d' % (product, values['price'], values['amount']))
    while not msvcrt.getch():
        pass
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'], MenuFunctions)


# функция для выбора как вывводить каталог для пользователя
def view_guest_catalog():
    with open('catalog.json', 'r', encoding='UTF-8') as catalog_r:
        catalog = json.load(catalog_r)
    if currentUser == {}:
        show_catalog(catalog)
    else:
        show_login_catalog(catalog)


# ФУНКЦИИ ПУНКТА МЕНЮ "ЗАКАЗЫ" ПОЛЬЗОВАТЕЛЯ
# функция для отображения конкретного заказа
def update_order(order):
    os.system("cls")
    print('Для выхода из заказа нажмите "q"')
    print('Номер заказа %06d' % order['id'])
    print('Дата и время создания заказа: %s' % order['date'])
    print('Количество товаров: %s' % get_order_products_amount(order))
    print('Товары:')
    for product, values in order['products'].items():
        print('%-15s Цена: %-4d Количество: %d' % (product, values['price'], values['amount']))
    print('Итоговая сумма заказа: %s' % get_order_sum(order))
    print('Статус заказа: %s' % order['status'])


# функция, реагиркющая на действия пользователя при отображении конкретного заказа
def view_order(order, user_order_list):
    update_order(order)
    pressedKey = None
    while pressedKey != button.q:  # q
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
    view_guest_orders(user_order_list.index(get_order_index(order, user_order_list)))


# функция,  которая обновляет меню заказов
def update_orders(currentRow):
    os.system("cls")
    user_orders_list = []
    print('Выберите заказ с помощью стрелок вверх/вниз и клавиши Enter')
    print('Для выхода нажмите "q"')
    print('Ваши заказы:')
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    for order in orders:
        if order['user'] == currentUser['login'] and order['status'] != status.CREATED:
            user_orders_list.append(order)
    if len(user_orders_list) == 0:
        print('Вы еще не совершили ни одного заказа, пройдите в каталог!')
    for order in user_orders_list:
        if currentRow == user_orders_list.index(order):
            print('\033[32m', end='')
        print('Номер заказа: %06d Дата и время: %s Количество товаров: %-3d Сумма: %-5d Статус: %s\033[0m' %
              (order['id'], order['date'], get_order_products_amount(order), get_order_sum(order), order['status']))
    return user_orders_list


# функция, реагирующая на действия пользователя в меню заказов
def view_guest_orders(currentRow=0):
    user_orders_list = update_orders(currentRow)
    pressedKey = None
    while pressedKey != button.q and (pressedKey != button.ENTER or len(user_orders_list) == 0):  # q
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            # down
            if pressedKey == button.DOWN and currentRow < len(user_orders_list) - 1:
                currentRow += 1
                user_orders_list = update_orders(currentRow)
            # up
            if pressedKey == button.UP and currentRow > 0:
                currentRow -= 1
                user_orders_list = update_orders(currentRow)
            if pressedKey == button.ENTER and len(user_orders_list) > 0:
                view_order(user_orders_list[currentRow], user_orders_list)
    show_menu(['Каталог', 'Заказы', 'Выйти из аккаунта'], MenuFunctions)


# ФУНКЦИИ АККАУНТА
# функция для авторизации пользователя
def authorize():
    with open('users.json', 'r', encoding='UTF-8') as users_r:
        usersFile = json.load(users_r)
    allLogins = list(map(lambda x: x['login'], usersFile))
    login = input("Введите логин: ")
    while not allLogins.__contains__(login):
        print('Пользователь не найден')
        login = input("Введите логин: ")
    password = input("Введите пароль: ")
    for user in usersFile:
        if user['login'] == login:
            correctPassword = user['password']
            while password != correctPassword:
                print('Неправильный пароль')
                password = input("Введите пароль: ")
            global currentUser
            currentUser = user
    show_menu(['Каталог', 'Заказы', 'Выйти из аккаунта'], MenuFunctions)


# функция для записи зарегистрированного пользователя в json
def write_to_users_json(newName, newLogin, newPassword):
    with open('users.json', 'r', encoding='UTF-8') as users_r:
        file = json.load(users_r)
    with open('users.json', 'w', encoding='UTF-8') as users_w:
        user_info = {'name': newName, 'login': newLogin, 'password': newPassword, 'role': 'guest'}
        file.append(user_info)
        json.dump(file, users_w, indent=2, ensure_ascii=False)


# функция для регистрации пользователя
def registration():
    newName = input("Введите свое имя: ")
    newLogin = input("Введите свой логин: ")
    newPassword = input("Введите свой пароль: ")
    newPasswordConfirm = input("Подтвердите пароль: ")
    while newPassword != newPasswordConfirm:
        newPassword = input("Введите свой пароль еще раз: ")
        newPasswordConfirm = input("Подтвердите пароль: ")
    write_to_users_json(newName, newLogin, newPassword)
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'], MenuFunctions)


# функция для выхода из аккаунта
def logout():
    global currentUser
    currentUser = {}
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'], MenuFunctions)

# ИНСТРУМЕНТЫ


currentUser = {}

# объявление словаря фунций меню (ключ - пункт меню, значение - функция)
MenuFunctions = {
                    'Регистрация': registration,
                    'Каталог': view_guest_catalog,
                    'Авторизация': authorize,
                    'Выйти из аккаунта': logout,
                    'Заказы': view_guest_orders,
                    'Выйти': exit
                }


def main():
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'], MenuFunctions)


main()
