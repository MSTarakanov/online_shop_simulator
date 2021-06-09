# подключим нужные библиотеки
import json
import os
import msvcrt
import cursor
import datetime as dt


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


def update_admin_catalog(catalog, currentRow, currentColumn):
    os.system("cls")
    print(f'Приветствуем, администратор {currentUser["name"]}')
    print('Для управления каталогом используются стрелки клавиатуры, для изменения нажмите Enter')
    print('Для выхода из каталога нажмите "q"')
    for product, values in catalog.items():
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


def is_amount_error(catalog):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    if is_cart_exist(orders):
        cart = get_cart(orders)
        if any(catalog[product]['amount'] < get_cart_product_amount(product) for product in
               cart.keys()):
            return True
    return False


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


def update_cart_prices(product_to_update, newPrice):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    for order in orders:
        if order['status'] == status.CREATED:
            for product, values in order['products'].items():
                if product == product_to_update:
                    values['price'] = newPrice
    with open('orders.json', 'w', encoding='UTF-8') as orders_w:
        json.dump(orders, orders_w, indent=2, ensure_ascii=False)


def change_catalog_value(catalog, currentRow, currentColumn):
    newValue = get_value()
    if currentColumn == 1:
        catalog[currentRow]['price'] = newValue
        update_cart_prices(currentRow, newValue)
    elif currentColumn == 2:
        catalog[currentRow]['amount'] = newValue
    with open('catalog.json', 'w', encoding='UTF-8') as catalog_w:
        json.dump(catalog, catalog_w, indent=2, ensure_ascii=False)
    return catalog


def show_login_catalog(catalog):
    currentRow = list(catalog.keys())[0]
    if currentUser['role'] == role.ADMIN:
        currentColumn = 1
    elif currentUser['role'] == role.GUEST:
        currentColumn = get_cart_product_amount(currentRow)
    pressedKey = None
    if currentUser['role'] == role.ADMIN:
        update_admin_catalog(catalog, currentRow, currentColumn)
    elif currentUser['role'] == role.GUEST:
        update_guest_catalog(catalog, currentRow, currentColumn)
    while pressedKey != button.q:  # q
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            # down
            if pressedKey == button.DOWN and currentRow != 'ok_btn':
                if (list(catalog.keys()).index(currentRow) < len(catalog) - 1 and currentUser['role'] == role.ADMIN) or \
                   (list(catalog.keys()).index(currentRow) < len(catalog) - int(get_cart_sum() == 0) and currentUser['role'] == role.GUEST):
                    try:
                        currentRow = list(catalog.keys())[list(catalog.keys()).index(currentRow) + 1]
                    except:
                        currentRow = 'ok_btn'
                    if currentUser['role'] == role.GUEST and currentRow != 'ok_btn':
                        currentColumn = get_cart_product_amount(currentRow)
            # up
            elif pressedKey == button.UP and currentRow != 'ok_btn' and list(catalog.keys()).index(currentRow) > 0:
                currentRow = list(catalog.keys())[list(catalog.keys()).index(currentRow) - 1]
                if currentUser['role'] == role.GUEST:
                    currentColumn = get_cart_product_amount(currentRow)
            elif pressedKey == button.UP and currentRow == 'ok_btn':
                currentRow = list(catalog.keys())[-1]
            # right
            elif pressedKey == button.RIGHT and currentRow != 'ok_btn' and ((currentUser['role'] == role.ADMIN and currentColumn < 2) or
                 currentUser['role'] == role.GUEST and currentColumn < catalog[currentRow]['amount']):
                currentColumn += 1
            # left
            elif pressedKey == button.LEFT and currentRow != 'ok_btn' and ((currentUser['role'] == role.ADMIN and currentColumn > 1) or
                                       (currentUser['role'] == role.GUEST and currentColumn > 0)):
                currentColumn -= 1
            # enter
            elif pressedKey == button.ENTER:
                if currentUser['role'] == role.ADMIN:
                    catalog = change_catalog_value(catalog, currentRow, currentColumn)
                elif currentUser['role'] == role.GUEST and currentRow == 'ok_btn':
                    accept_order(catalog)
                    currentRow = list(catalog.keys())[-1]
                    currentColumn = 0
            if currentUser['role'] == role.ADMIN:
                update_admin_catalog(catalog, currentRow, currentColumn)
            elif currentUser['role'] == role.GUEST:
                update_guest_catalog(catalog, currentRow, currentColumn)
    if currentUser['role'] == role.ADMIN:
        show_menu(['Каталог', 'Заказы', 'Выйти из аккаунта'])
    elif currentUser['role'] == role.GUEST:
        show_menu(['Каталог', 'Заказы', 'Выйти из аккаунта'])

def change_cart_status():
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    for order in orders:
        if order['status'] == status.CREATED:
            order['status'] = status.PAID
            user_order = order
    with open('orders.json', 'w', encoding='UTF-8') as orders_w:
        json.dump(orders, orders_w, indent=2, ensure_ascii=False)
    return user_order


def update_products_amount(user_order, catalog):
    for product, values in user_order['products'].items():
        catalog[product]['amount'] -= values['amount']
    with open('catalog.json', 'w', encoding='UTF-8') as catalog_w:
        json.dump(catalog, catalog_w, indent=2, ensure_ascii=False)

def accept_order(catalog):
    user_order = change_cart_status()
    update_products_amount(user_order, catalog)


def show_catalog(catalog):
    print('Для возможности взаимодействия с каталогом авторизуйтесь')
    print('Для выхода из каталога нажмите любую клавишу')
    for product, values in catalog.items():
        print('%-15s Цена: %-4d Количество: %d' % (product, values['price'], values['amount']))
    while not msvcrt.getch():
        pass
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'])


def get_max_id(orders):
    max_id = 0
    for order in orders:
        if order['id'] > max_id:
            max_id = order['id']
    return max_id


def is_cart_exist(orders):
    if any(order['user'] == currentUser['login'] and order['status'] == status.CREATED for order in orders):
        return True
    return False


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


def get_cart(orders):
    for order in orders:
        if order['user'] == currentUser['login'] and order['status'] == status.CREATED:
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
    elif currentUser['role'] == role.GUEST or currentUser['role'] == role.ADMIN:
        show_login_catalog(catalog)


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
    show_menu(['Каталог', 'Заказы', 'Выйти из аккаунта'])


def logout():
    global currentUser
    currentUser = {}
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'])


def get_cart_sum():
    cart_sum = 0
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    if is_cart_exist(orders):
        cart = get_cart(orders)
        for values in cart.values():
            cart_sum += values['price'] * values['amount']
    return cart_sum


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


def update_orders(currentRow):
    os.system("cls")
    user_orders_list = []
    print('Ваши заказы')
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    for order in orders:
        if (currentUser['role'] == role.GUEST and order['user'] == currentUser['login'] and order['status'] != status.CREATED) or \
           (currentUser['role'] == role.ADMIN and order['status'] != status.CREATED):
            user_orders_list.append(order)
    if len(user_orders_list) == 0:
        print('Вы еще не совершили ни одного заказа, пройдите в каталог!')
    for order in user_orders_list:
        if currentRow == user_orders_list.index(order):
            print('\033[32m', end='')
        print('Номер заказа: %06d Дата и время: %s Количество товаров: %-3d Сумма: %-5d Статус: %s\033[0m' %
              (order['id'], order['date'], get_order_products_amount(order), get_order_sum(order), order['status']))
    return user_orders_list


def get_status():
    return show_menu(['Отправлен', 'Доставлен'])


def change_order_status(order_to_update):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    for order in orders:
        if order == order_to_update:
            order['status'] = get_status()
            ret = order
    with open('orders.json', 'w', encoding='UTF-8') as orders_w:
        json.dump(orders, orders_w, indent=2, ensure_ascii=False)
    return ret


def view_order(order, user_order_list):
    update_order(order)
    pressedKey = None
    while pressedKey != button.q:  # q
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            # enter
            if pressedKey == button.ENTER and currentUser['role'] == role.ADMIN:
                order = change_order_status(order)
                update_order(order)
    view_orders(user_order_list.index(get_order_index(order, user_order_list)))


def get_order_index(find_to_order, user_order_list):
    for order in user_order_list:
        if order['id'] == find_to_order['id']:
             return order


def update_order(order):
    os.system("cls")
    if currentUser['role'] == role.ADMIN:
        print('Пользователь: %s' % order['user'])
    print('Номер заказа %06d' % order['id'])
    print('Дата и время создания заказа: %s' % order['date'])
    print('Количество товаров: %s' % get_order_products_amount(order))
    print('Товары:')
    for product, values in order['products'].items():
        print('%-15s Цена: %-4d Количество: %d' % (product, values['price'], values['amount']))
    print('Итоговая сумма заказа: %s' % get_order_sum(order))
    print('Статус заказа: %s' % order['status'])


def view_orders(currentRow=0):
    user_orders_list = update_orders(currentRow)
    pressedKey = None
    while pressedKey != button.q and pressedKey != button.ENTER:  # q
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
            if pressedKey == button.ENTER:
                if currentUser['role'] == role.GUEST:
                    view_order(user_orders_list[currentRow], user_orders_list)
                elif currentUser['role'] == role.ADMIN:
                    view_order(user_orders_list[currentRow], user_orders_list)

    show_menu(['Каталог', 'Заказы', 'Выйти из аккаунта'])

def delivered_status():
    return status.DELIVERED

def sent_status():
    return status.SENT

menuFunctions = {'Регистрация': registration,
                 'Каталог': view_catalog,
                 'Авторизация': authorize,
                 'Выйти из аккаунта': logout,
                 'Заказы': view_orders,
                 'Доставлен': delivered_status,
                 'Отправлен': sent_status,
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


# основная функция
def main():
    cursor.hide()
    show_menu(['Каталог', 'Авторизация', 'Регистрация', 'Выйти'])
    cursor.show()


main()


# управляющие RED_TEXT = \033m[0

# на ку выходит отовсюду
# добавить инструкции во все меню
