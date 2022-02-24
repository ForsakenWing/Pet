import sqlite3 as sq

from config import db_name

base = sq.connect(db_name)
cur = base.cursor()


def sql_start():
    if base:
        print("Database connected")
    cur.execute('CREATE TABLE IF NOT EXISTS users_data(user_id INTEGER NOT NULL PRIMARY KEY, '
                'first_name TEXT, phone_number INTEGER, '
                'email TEXT, latitude REAL, longitude REAL)')
    base.commit()


async def sql_add(state):
    async with state.proxy() as data:
        if not data['user_id'] in sql_get_users_id():
            del data['language']
            cur.execute('INSERT INTO users_data VALUES (?, ?, ?, ?, ?, ?)', tuple(data.values()))
            base.commit()
            return True
        else:
            return False


async def sql_del(state):
    async with state.proxy() as data:
        user_id_to_del = (data['user_id'],)
        cur.execute('DELETE FROM users_data WHERE user_id == ?', user_id_to_del)
        base.commit()


def sql_get_users_id():
    users_id = sum(cur.execute('SELECT user_id from users_data').fetchall(), tuple())
    return users_id


async def sql_update(state, key, new_data, user_id):
    async with state.proxy():
        cur.execute(f'UPDATE users_data SET {key} == ? WHERE user_id == ?',
                    (new_data, user_id))
        base.commit()

