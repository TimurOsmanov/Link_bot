import sqlite3


def get_file_number():
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        select_info = 'select unique_id from Link_info'
        cursor.execute(select_info)
        number = cursor.fetchall()
    return number[-1][0]


def get_voice_number():
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        select_info = 'select unique_id from Voice_info'
        cursor.execute(select_info)
        number = cursor.fetchall()
    return number[-1][0]


def create_db_and_files_table():
    try:
        with sqlite3.connect('link.db') as conn:
            cursor = conn.cursor()
            create_table = '''create table Link_info (
            unique_id integer primary key, 
            user_id integer, 
            name text)'''
            cursor.execute(create_table)
        file_num = 0
        return file_num
    except sqlite3.Error as error_Link_info_exists:
        if error_Link_info_exists.args == ('table Link_info already exists',):
            print(f"Напоминаю, таблица уже создана {error_Link_info_exists}")
            try:
                file_num = get_file_number()
            except IndexError:
                # IndexError raises when table is empty
                file_num = 0
            return file_num
        else:
            print("Ошибка при подключении к sqlite", error_Link_info_exists)


def create_users_table():
    try:
        with sqlite3.connect('link.db') as conn:
            cursor = conn.cursor()
            create_table = '''create table Users_info (
            user_id integer primary key, 
            user_text_id text,
            type integer)'''
            cursor.execute(create_table)
    except sqlite3.Error as error_users_info_exists:
        # error_workers_info_exists.args ('table workers_info already exists',)
        # is a system message when your DB already has table
        if error_users_info_exists.args == ('table Users_info already exists',):
            print(f"Напоминаю, таблица уже создана {error_users_info_exists}")


def create_voice_table():
    try:
        with sqlite3.connect('link.db') as conn:
            cursor = conn.cursor()
            create_table = '''create table Voice_info (
            unique_id integer primary key, 
            user_id integer, 
            name text)'''
            cursor.execute(create_table)
        voice_num = 0
        return voice_num
    except sqlite3.Error as error_Voice_info_exists:
        if error_Voice_info_exists.args == ('table Voice_info already exists',):
            print(f"Напоминаю, таблица уже создана {error_Voice_info_exists}")
            try:
                voice_num = get_voice_number()
            except IndexError:
                # IndexError raises when table is empty
                voice_num = 0
            return voice_num
        else:
            print("Ошибка при подключении к sqlite", error_Voice_info_exists)


def get_users_list():
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        select_info = 'select distinct user_id from Users_info'
        cursor.execute(select_info)
        users = cursor.fetchall()
        return [user[0] for user in users]


def add_user(data_tuple):
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        insert_info = 'insert into Users_info values (?, ?, ?)'
        cursor.execute(insert_info, data_tuple)


def get_translators_id():
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        select_info = """select distinct user_id from Users_info where type = '1'"""
        cursor.execute(select_info)
        translator = cursor.fetchone()
        return translator[0] if translator else None


def update_user_status(user, user_type):
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        update_info = f"update Users_info set type = {user_type} where user_id = {user}"
        cursor.execute(update_info)


def get_files_names():
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        select_info = """select distinct name from Link_info"""
        cursor.execute(select_info)
        names = cursor.fetchall()
        return [name[0] for name in names]


def add_file(data_tuple):
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        insert_info = 'insert into Link_info values (?, ?, ?)'
        cursor.execute(insert_info, data_tuple)


def add_voice(data_tuple):
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        insert_info = 'insert into Voice_info values (?, ?, ?)'
        cursor.execute(insert_info, data_tuple)


def get_receiver_id(file_name):
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        select_info = f"""select user_id from Link_info where name = '{file_name}'"""
        cursor.execute(select_info)
        return cursor.fetchone()[0]


def get_receiver_text_id(user_id):
    with sqlite3.connect('link.db') as conn:
        cursor = conn.cursor()
        select_info = f"""select user_text_id from Users_info where user_id = '{user_id}'"""
        cursor.execute(select_info)
        return cursor.fetchone()[0]
