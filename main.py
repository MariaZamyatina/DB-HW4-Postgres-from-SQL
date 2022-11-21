import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def search_id_user_contact(cur, name, surname):
    """ Метод возвращает id пользователя"""
    cur.execute("""
                    SELECT id FROM user_contact
                    WHERE name = %s AND surname = %s;
                    """, (name, surname))
    return cur.fetchone()


def create_user(cur, name, surname, mail, number):
    """
    Функция создает пользователя, вносит его имя и контакты в БД
        """
    cur.execute("""
                CREATE TABLE IF NOT EXISTS user_contact(
                id SERIAL PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                surname VARCHAR(40) NOT NULL,
                mail  VARCHAR(40) NOT NULL);
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS user_number(
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES user_contact(id),
                number VARCHAR(12));
                """)

    cur.execute("""
                INSERT INTO user_contact(name,surname,mail) 
                VALUES(%s, %s, %s);                
                """, (name, surname, mail))
    conn.commit()

    if len(number) > 0:
        number = number.split(",")
        id_user = search_id_user_contact(cur, name, surname)
        for i in number:
            update_number(cur, i, id_user)
    conn.commit()


def update_number(cur, n, id):
    """Метод добавляет номер телефона к данным существующего пользователя"""
    while True:
        try:
            cur.execute("""
                        INSERT INTO user_number(user_id, number)
                        VALUES(%s, %s);                
                        """, (id, n))
            conn.commit()
            print('\nНомер добавлен\n')
            break

        except:
            print('\nОшибка. Проверьте корректность номера.\n')
            break



def change(cur, object, new_data, id_user):
    """ Метод изменяет данные пользователя"""
    while True:
        try:
            if object == 'name':
                cur.execute("""
                                UPDATE user_contact
                                SET name = %s
                                WHERE id = %s""", (new_data, id_user))

            elif object == 'surname':
                cur.execute("""
                                UPDATE user_contact
                                SET surname = %s
                                WHERE id = %s""", (new_data, id_user))

            elif object == 'mail':
                cur.execute("""
                                UPDATE user_contact
                                SET mail = %s
                                WHERE id = %s""", (new_data, id_user))

            print('Данные изменены')
            conn.commit()
            break
        except:
            print('Error')
            break


def delete_number(cur, id_user):
    """ Метод удаляет выбранный номер пользователя"""
    while True:
        try:
            cur.execute("""
                            SELECT id, number FROM user_number
                            WHERE user_id = %s""", (id_user,)
                        )
            data = cur.fetchall()
            if data == []:
                print('Номеров нет')
                break
            else:
                for i in data:
                    print(f'id: {i[0]}, номер: {i[1]}')
                n = int(input('Укажите id номера, который нужно удалить'))
                cur.execute("""DELETE FROM user_number
                                WHERE id = %s""", (n,))

                print('Номер удален')
                conn.commit()
                break
        except:
            print('Error')
            break


def delete_user(cur, id_user):
    """ Метод удаляет существующего пользователя"""
    while True:
        try:
            cur.execute("""
                        DELETE FROM user_number
                        WHERE user_id = %s""", (id_user,)
                        )
            conn.commit()
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


def search_datauser(cur, name, surname):
    """ Метод возвращает данные пользователя по его id"""
    while True:
        try:
            cur.execute("""
                        SELECT user_contact.id,name,surname,mail,number FROM user_contact
                        FULL JOIN user_number un ON user_contact.id = un.user_id                        
                        WHERE name = %s AND surname = %s""", (name, surname))
            data = cur.fetchall()
            return data
        except:
            print("error")
            break


if __name__ == '__main__':
    database = os.getenv('database')
    user = os.getenv('user')
    password = os.getenv('password')
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
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
                        #id_user = search_id_user_contact(cur, name, surname)
                        # user = search_datauser(cur, name, surname)
                        #
                        # if user != []:
                        n = input("Будете указывать номер пользователя? (yes/no): ")
                        if n == "yes":
                            number = input('Введите номера пользователя (если несколько номеров - через запятую): ')
                        else:
                            number = ""

                        print(
                            f'Данные нового клиента: \n Имя: {name}\n Фамилия: {surname}\n mail: {mail}\n Номер(а): {number}')
                        a = input('Записать нового клиента в базу? (yes/no): ')
                        if a.lower() != 'yes':
                            print('\nПользователь не записан\n')
                            break
                        else:
                            while True:
                                try:
                                    print(number)
                                    create_user(cur, name, surname, mail, number)
                                    print('\nДанные успешно записаны\n')
                                    break
                                except:
                                    print(
                                        '\nПользователь записан. Ошибка в номере. Длина номера не должна превышать 12 символов.\n')
                                    break
                            break


                elif choice == '2':
                    while True:
                        s = input('Укажите фамилию пользователя: ')
                        n = input('Укажите имя пользователя: ')
                        number = input('Введите номер, который нужно добавить: ')
                        id_user = search_id_user_contact(cur, n, s)  # возвращает id пользователя
                        if id_user is None:  # Пользователь не найден
                            break
                        else:
                            update_number(cur, number, id_user)
                            break

                elif choice == '3':
                    while True:
                        print('\nДанные какого пользователя требуется изменить?')
                        s = input('Укажите фамилию пользователя: ')
                        n = input('Укажите имя пользователя: ')
                        id_user = search_id_user_contact(cur, n, s)
                        if id_user is None:  # Пользователь не найден
                            print('Пользователь не найден')
                            break
                        else:
                            dict = {1: 'name', 2: 'surname', 3: 'mail', 4: 'выход'}
                            print(f'1 - {dict[1]}\n'
                                  f'2 - {dict[2]}\n'
                                  f'3 - {dict[3]}\n'
                                  f'4 - {dict[4]}')
                            vibor = int(input('Какие данные требуется изменить: '))
                            if vibor == '4':
                                break
                            new_data = input('Введите новые данные: ')
                            change(cur, dict[vibor], new_data, id_user)
                            break

                elif choice == '4':
                    while True:
                        print('\nНомер какого пользователя требуется удалить?')
                        s = input('Укажите фамилию пользователя: ')
                        n = input('Укажите имя пользователя: ')
                        id_user = search_id_user_contact(cur, n, s)
                        if id_user is None:  # Пользователь не найден
                            print('Пользователь не найден')
                            break
                        else:
                            delete_number(cur, id_user)
                            break

                elif choice == '5':
                    while True:
                        try:
                            print('\nДанные какого пользователя требуется удалить?')
                            surname = input('Укажите фамилию пользователя: ')
                            name = input('Укажите имя пользователя: ')
                            # id_user = search_id_user_contact(cur, n, s)
                            data = search_datauser(cur, name, surname)
                            if data != []:
                                for i in data:
                                    print('Данные клиента: ', *i)
                                id = input('Подтвердите удаление пользователя. Укажите его id: ')
                                delete_user(cur, int(id))

                                break
                            else:
                                print("Клиент не найден")
                                break
                        except:
                            print('Error')
                            break
                elif choice == '6':
                    while True:
                        surname = input('Укажите фамилию пользователя: ')
                        name = input('Укажите имя пользователя: ')
                        data = search_datauser(cur, name, surname)
                        if data != []:
                            for i in data:
                                print('Данные клиента: ', *i)
                            break
                        else:
                            print("Клиент не найден")
                            break
                else:
                    break
