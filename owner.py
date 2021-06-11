from common import os, json, msvcrt
from common import currentUser, role, status, button
from common import show_menu, get_order_products_amount, get_order_sum, get_order_index, get_status


def update_order(order):
    os.system("cls")
    print(order)
    print('Для выхода из заказа нажмите "q"')
    print('Для изменения статуса заказа нажмите Enter и выберите статус')
    print('Пользователь: %s' % order['user'])
    print('Номер заказа %06d' % order['id'])
    print('Дата и время создания заказа: %s' % order['date'])
    print('Количество товаров: %s' % get_order_products_amount(order))
    print('Товары:')
    for product, values in order['products'].items():
        print('%-15s Цена: %-4d Количество: %d' % (product, values['price'], values['amount']))
    print('Итоговая сумма заказа: %s' % get_order_sum(order))
    print('Статус заказа: \033[32m%s\033[0m' % order['status'])


def change_order_status(order_to_update):
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    for order in orders:
        if order == order_to_update:
            order['status'] = get_status(menuFunctions)
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
            if pressedKey == button.ENTER:
                order = change_order_status(order)
                update_order(order)
    view_owner_orders(user_order_list.index(get_order_index(order, user_order_list)))


def update_orders(currentRow):
    os.system("cls")
    user_orders_list = []
    print('Выберите заказ с помощью стрелок вверх/вниз и клавиши Enter')
    print('Для выхода нажмите "q"')
    with open('orders.json', 'r', encoding='UTF-8') as orders_r:
        orders = json.load(orders_r)
    for order in orders:
        if order['status'] != status.CREATED:
            user_orders_list.append(order)
    if len(user_orders_list) == 0:
        print('Посетители еще не сделали ни одного заказа')
    for order in user_orders_list:
        if currentRow == user_orders_list.index(order):
            print('\033[32m', end='')
        print('Номер заказа: %06d Дата и время: %s Количество товаров: %-3d Сумма: %-5d Статус: %s\033[0m' %
              (order['id'], order['date'], get_order_products_amount(order), get_order_sum(order), order['status']))
    return user_orders_list

def view_owner_orders(currentRow=0):
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
                view_order(user_orders_list[currentRow], user_orders_list)
    show_menu(['Каталог', 'Заказы', 'Выйти'], menuFunctions)


# функции для отображения каталога для владельца

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


def show_login_admin_catalog(catalog):
    currentRow = list(catalog.keys())[0]
    currentColumn = 1
    pressedKey = None
    update_admin_catalog(catalog, currentRow, currentColumn)
    while pressedKey != button.q:  # q
        pressedKey = None
        while pressedKey is None:
            pressedKey = ord(msvcrt.getch())
            print(pressedKey)
            # down
            if pressedKey == button.DOWN and list(catalog.keys()).index(currentRow) < len(catalog) - 1:
                currentRow = list(catalog.keys())[list(catalog.keys()).index(currentRow) + 1]
            # up
            elif pressedKey == button.UP and list(catalog.keys()).index(currentRow) > 0:
                currentRow = list(catalog.keys())[list(catalog.keys()).index(currentRow) - 1]
            # right
            elif pressedKey == button.RIGHT and currentColumn < 2:
                currentColumn += 1
            # left
            elif pressedKey == button.LEFT and currentColumn > 1:
                currentColumn -= 1
            # enter
            elif pressedKey == button.ENTER:
                catalog = change_catalog_value(catalog, currentRow, currentColumn)
            update_admin_catalog(catalog, currentRow, currentColumn)
    show_menu(['Каталог', 'Заказы', 'Выйти'], menuFunctions)


# функции, показывающие каталог
def show_catalog(catalog):
    print('Для возможности взаимодействия с каталогом авторизуйтесь')
    print('Для выхода из каталога нажмите любую клавишу')
    for product, values in catalog.items():
        print('%-15s Цена: %-4d Количество: %d' % (product, values['price'], values['amount']))
    while not msvcrt.getch():
        pass
    show_menu(['Каталог', 'Заказы', 'Выйти'], menuFunctions)


def view_owner_catalog():
    with open('catalog.json', 'r', encoding='UTF-8') as catalog_r:
        catalog = json.load(catalog_r)
    show_login_admin_catalog(catalog)


# возвращают один из статусов, чтобы можно было выбрать через меню
def delivered_status():
    return status.DELIVERED


def sent_status():
    return status.SENT


def paid_status():
    return status.PAID


menuFunctions = {'Каталог': view_owner_catalog,
                 'Заказы': view_owner_orders,
                 'Доставлен': delivered_status,
                 'Отправлен': sent_status,
                 'Оплачен': paid_status,
                 'Выйти': exit}

currentUser = {
                "name": "Валерия",
                "login": "admin",
                "password": "admin",
                "role": "admin"
            }


def main():
    show_menu(['Каталог', 'Заказы', 'Выйти'], menuFunctions)


main()
