import json

def write_to_users_json(newName, newLogin, newPassword):
    with open('users.json', 'r', encoding='UTF-8') as users_r:
        file = json.load(users_r)
    with open('users.json', 'w', encoding='UTF-8') as users_w:
        target = file['users']
        user_info = {'name': newName, 'login': newLogin, 'password': newPassword, 'role': 'guest'}
        target.append(user_info)
        json.dump(file, users_w, indent=2, ensure_ascii=False)



