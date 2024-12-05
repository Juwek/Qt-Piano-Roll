import sqlite3
from pydub import AudioSegment


BASE = 'base.sqlite'


def get_logins_from_user():
    bd = sqlite3.connect(BASE)
    cur = bd.cursor()
    logins = [i[0] for i in cur.execute("""SELECT login FROM user""").fetchall()]
    bd.close()
    return logins


def register_user(login: str, password: str):
    if login not in get_logins_from_user():
        data = (str(login), str(password))
        bd = sqlite3.connect(BASE)
        cur = bd.cursor()
        cur.execute("""INSERT INTO user(login, password) VALUES(?, ?)""", data)
        bd.commit()
        bd.close()
        return 1
    else:
        return 2


def check_user_for_password(login: str, password: str):
    if login not in get_logins_from_user():
        return 2
    else:
        bd = sqlite3.connect(BASE)
        cur = bd.cursor()
        base_password = cur.execute("""SELECT password FROM user
                        WHERE login = ?""", (str(login),)).fetchall()
        bd.close()
        if password != base_password[0][0]:
            return 3
        else:
            return 1


def get_table(login: str, name: str):
    bd = sqlite3.connect(BASE)
    cur = bd.cursor()
    table = cur.execute("""SELECT table_items, bytes FROM [table]
                    WHERE name = ? AND login = ?""", (str(name), str(login))).fetchall()
    bd.close()
    return table


def get_names_tables(login: str):
    bd = sqlite3.connect(BASE)
    cur = bd.cursor()
    names = cur.execute("""SELECT DISTINCT name FROM [table]
                        WHERE login = ?""", (str(login),)).fetchall()
    bd.close()
    return names


def update_name(login: str, last_name: str, new_name: str):
    data = (str(new_name), str(last_name), str(login))
    bd = sqlite3.connect(BASE)
    cur = bd.cursor()
    cur.execute("""UPDATE table SET name = ?
                    WHERE name = ? AND login = ?""", data)
    bd.close()


def add_table(login: str, name: str, table_items: str, b: bytes):
    data = (str(login), str(name), str(table_items), b)
    bd = sqlite3.connect(BASE)
    cur = bd.cursor()
    cur.execute("""INSERT INTO [table](login, name, table_items, bytes) VALUES(?, ?, ?, ?)""", data)
    bd.commit()
    bd.close()


def delete_table(login: str, name: str):
    bd = sqlite3.connect(BASE)
    cur = bd.cursor()
    cur.execute("""DELETE FROM [table]
                    WHERE login = ? AND name = ?""", (str(login), str(name)))
    bd.commit()
    bd.close()