import psycopg2


def create_user(conn, name, surname, mail, number):
    """
    Функция создает пользователя, вносит его имя и контакты в БД
        """
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_contact(
                id SERIAL PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                surname VARCHAR(40) NOT NULL,
                mail  VARCHAR(40) NOT NULL,
                number VARCHAR(12)
            );
            """)

        cur.execute("""
            INSERT INTO user_contact(name,surname,mail,number) 
            VALUES(%s, %s, %s, %s);                
            """, (name, surname, mail, number))
        conn.commit()


def searh_id_user(conn, name, surname):
    """ Метод возвращает id пользователя по имени и фамилии"""
    with conn.cursor() as cur:
        while True:
            try:
                cur.execute("""
                    SELECT * FROM user_contact                            
                    WHERE name = %s AND surname = %s;
                    """, (name, surname))
                data = cur.fetchall()
                if data == []:
                    print('Пользователь не найден')
                    return None
                if len(data) > 1:
                    print('Данные пользователя(ей): ')
                    for i in data:
                        print(f'id: {i[0]}, {i[1]} {i[2]}, {i[3]}, номер(а): {", ".join(i[4])}')
                    id_user = input('Укажите id нужного пользователя: ')
                    return id_user
                else:
                    id_user = data[0][0]
                    return id_user
            except TypeError:
                print('\nПользователь с таким именем/фамилией не найден\n')
                break


def update_number(conn, n, id):
    """Метод добавляет номер телефона к данным существующего пользователя"""
    with conn.cursor() as cur:
        while True:
            try:
                cur.execute("""UPDATE user_contact
                                SET number = number|| ARRAY[%s]
                                WHERE id = %s""", (n, id))
                conn.commit()
                print('\nНомер добавлен\n')
                break
            except:
                print('\nОшибка. Проверьте корректность номера.\n')
                break


def change(conn, object, new_data, id_user):
    """ Метод изменяет данные пользователя"""
    with conn.cursor() as cur:
        while True:
            try:
                if object == 'name':
                    cur.execute("""
                                UPDATE user_contact
                                SET name = %s
                                WHERE id = %s""", (new_data, id_user))
                    conn.commit()
                elif object == 'surname':
                    cur.execute("""
                                UPDATE user_contact
                                SET surname = %s
                                WHERE id = %s""", (new_data, id_user))
                    conn.commit()
                elif object == 'mail':
                    cur.execute("""
                                UPDATE user_contact
                                SET mail = %s
                                WHERE id = %s""", (new_data, id_user))
                    conn.commit()
                else:
                    cur.execute("""
                                UPDATE user_contact
                                SET number = ARRAY[%s]
                                WHERE id = %s""", (new_data, id_user))
                    conn.commit()
                    print('Данные успешно изменены.\n')
                    break
            except:
                print('Error')
                break


def delete_number(conn, id_user):
    """ Метод удаляет выбранный номер пользователя"""
    with conn.cursor() as cur:
        while True:
            try:
                cur.execute("""
                            SELECT number FROM user_contact
                            WHERE id = %s""", (id_user,)
                            )
                data = cur.fetchall()[0][0]
                if data:
                    count = 1
                    list = []
                    print('Список Номеров:')
                    for i in data:
                        print(f"{count} - ", i)
                        list.append(i)
                        count += 1
                else:
                    print('\nНомеров нет\n')
                    break
                num = int(input('Какой номер нужно удалить?: '))
                list.pop(num - 1)
                cur.execute("""UPDATE user_contact
                            SET number = %s
                            WHERE id = %s""", (list, id_user))
                conn.commit()
                print('\nНомер успешно удален\n')
                break
            except:
                print('Error')
                break


def delete_user(conn, id_user):
    """ Метод удаляет существующего пользователя"""
    with conn.cursor() as cur:
        while True:
            try:
                cur.execute("""
                            DELETE FROM user_contact
                            WHERE id = %s""", (id_user,)
                            )
                conn.commit()
                print('Пользователь удален\n')
                break
            except:
                print('Error')
                break


def search_datauser(conn, id_user):
    """ Метод возвращает данные пользователя по его id"""
    with conn.cursor() as cur:
        while True:
            try:
                cur.execute("""
                            SELECT name,surname,mail,number FROM user_contact
                            WHERE id = %s""", (id_user,))
                data = cur.fetchall()[0]
                list = []
                for i in data:
                    list.append(i)
                st = ",".join(list[-1])
                list.pop(-1)
                list.append(st)
                table_data = [['NAME', 'SURNAME', 'EMAIL', 'NUMBER'], list]
                print_pretty_table(table_data)
                break
            except:
                print('error')
                break


def print_pretty_table(data, cell_sep=' | ', header_separator=True):
    """ Метод выводит данные пользователя в таблице"""
    rows = len(data)
    cols = len(data[0])
    col_width = []
    for col in range(cols):
        columns = [data[row][col] for row in range(rows)]
        col_width.append(len(max(columns, key=len)))
    separator = "-+-".join('-' * n for n in col_width)
    for i, row in enumerate(range(rows)):
        if i == 1 and header_separator:
            print(separator)
        result = []
        for col in range(cols):
            item = data[row][col].rjust(col_width[col])
            result.append(item)
        print(cell_sep.join(result))
        print()

database = input('ведите название БД: ')
user = input('введите логин: ')
password = input('пароль: ')
with psycopg2.connect(database=database, user=user, password=password) as conn:
    while True:
        print('\nУправление данными клиента: ')
        dict = {1: 'Добавление нового пользователя',
                2: 'Добавление номера телефона пользователя',
                3: 'Изменение данных клиента',
                4: 'Удаление номера телефона пользователя',
                5: 'Удаление существующего пользователя',
                6: 'Поиск клиента по его данным',
                7: 'Выход'}
        print(f'1 - {dict[1]}\n'
              f'2 - {dict[2]}\n'
              f'3 - {dict[3]}\n'
              f'4 - {dict[4]}\n'
              f'5 - {dict[5]}\n'
              f'6 - {dict[6]}\n'
              f'7 - {dict[7]}\n')
        choice = input('Введите нужный вариант: ')

        if choice == '1':
            while True:
                surname = input('Введите фамилию пользователя: ')
                name = input('Введите имя пользователя: ')
                mail = input('Введите mail пользователя: ')
                number = input('Введите номера пользователя (если несколько номеров - через запятую): ')
                print(f'Данные нового клиента: \n Имя: {name}\n Фамилия: {surname}\n mail: {mail}\n Номер(а): {number}')

                a = input('Записать нового клиента в базу? (yes/no): ')
                if a.lower() != 'yes':
                    print('\nПользователь не записан\n')
                    break
                else:
                    while True:
                        try:
                            create_user(conn,name, surname, mail, number.split(','))
                            print('\nДанные успешно записаны\n')
                            break
                        except:
                            print('\nОшибка. Длина номера не должна превышать 12 символов.\n')
                            break
                    break

        elif choice == '2':
            while True:
                s = input('Укажите фамилию пользователя: ')
                n = input('Укажите имя пользователя: ')
                number = input('Введите номер, который нужно добавить: ')
                id_user = searh_id_user(conn, n, s)  # возвращает id пользователя
                if id_user is None:  # Пользователь не найден
                    break
                else:
                    update_number(conn, number, id_user)
                    break

        elif choice == '3':
            while True:
                print('\nДанные какого пользователя требуется изменить?')
                s = input('Укажите фамилию пользователя: ')
                n = input('Укажите имя пользователя: ')
                id_user = searh_id_user(conn, n, s)
                if id_user is None:  # Пользователь не найден
                    break
                else:
                    dict = {1: 'name', 2: 'surname', 3: 'mail', 4: 'number', 5: 'выход'}
                    print(f'1 - {dict[1]}\n'
                          f'2 - {dict[2]}\n'
                          f'3 - {dict[3]}\n'
                          f'4 - {dict[4]}\n'
                          f'5 - {dict[5]}')
                    vibor = int(input('Какие данные требуется изменить: '))
                    new_data = input('Введите новые данные: ')
                    change(conn, dict[vibor], new_data, id_user)
                    break

        elif choice == '4':
            while True:
                print('\nНомер какого пользователя требуется удалить?')
                s = input('Укажите фамилию пользователя: ')
                n = input('Укажите имя пользователя: ')
                id_user = searh_id_user(conn, n, s)
                if id_user is None:  # Пользователь не найден
                    break
                else:
                    delete_number(conn, id_user)
                    break

        elif choice == '5':
            while True:
                try:
                    print('\nДанные какого пользователя требуется удалить?')
                    s = input('Укажите фамилию пользователя: ')
                    n = input('Укажите имя пользователя: ')
                    id_user = searh_id_user(conn, n, s)
                    if id_user is None:
                        break
                    else:
                        c = input(f'Подтвердите удаление пользователя {s} {n} (yes/no): ')
                        if c.lower() == 'yes':
                            delete_user(conn, id_user)
                            break
                        else:
                            break
                except:
                    print('Error')
                    break
        elif choice == '6':
            while True:
                s = input('Укажите фамилию пользователя: ')
                n = input('Укажите имя пользователя: ')
                id_user = searh_id_user(conn, n, s)
                if id_user is None:
                    break
                else:
                    search_datauser(conn, id_user)
                    break
        else:
            break
conn.close()
