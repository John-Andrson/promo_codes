from sshtunnel import SSHTunnelForwarder
import pymysql


class DatabaseManager:
    # создание поля для хранения экземпляра класса
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    # инициализация БД
    def _init_db(self, host='127.0.0.1', user='goldman', password='qweasdqwe1', database='promo_data'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    # функция подключения к БД
    def connect_to_database(self):
        while True:
            try:
                # создание туннеля
                self.tunnel = SSHTunnelForwarder(
                    ("192.168.0.231", 22),
                    ssh_username=self.user,
                    ssh_password=self.password,
                    remote_bind_address=('127.0.0.1', 3306)
                )
                self.tunnel.start()

                # подключение к БД
                self.connection = pymysql.connect(
                    host=self.host,
                    port=self.tunnel.local_bind_port,
                    # port=3306,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                self.cursor = self.connection.cursor()  # Создаем курсор
                return self.connection
            except pymysql.Error as e:
                import time
                # Дождитесь перед следующей попыткой
                time.sleep(1)

    # функция завершения сеанса подключения к БД
    def close_connection(self):
        self.cursor.close()
        self.connection.close()
        self.tunnel.stop()

    # добавление новых пользователей
    def add_users(self, u_id, u_name, u_nick):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных
        try:
            check_user_id = "SELECT u_id FROM profile WHERE u_id = %s"
            self.cursor.execute(check_user_id, u_id)
            result = self.cursor.fetchone()
            if result is None:
                sql_query = "INSERT INTO profile (u_id, u_name, u_nick) VALUES (%s, %s, %s)"
                user_data = (u_id, u_name, u_nick)

                self.cursor.execute(sql_query, user_data)
                self.connection.commit()

        finally:
            self.close_connection()

    # добавление новых промокодов
    def add_new_codes(self, p_section, p_store, p_code, p_description, p_date):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных
        try:
            sql_query = "INSERT INTO codes (p_section, p_store, p_code, p_description, p_date, p_status)" \
                        "VALUES (%s, %s, %s, %s, %s, %s)"
            user_data = (p_section, p_store, p_code, p_description, p_date, 1)

            self.cursor.execute(sql_query, user_data)
            self.connection.commit()
            return "Промокод успешно добавлен!"
        except Exception as e:
            return f"Ошибка при добавлении промокода: {e}"

        finally:
            self.close_connection()

    # фильтрация записей
    def search_records(self, p_section, p_store, p_date):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных
        try:
            if p_date == "Не указывать дату":
                sql_query = "SELECT p_id, p_code, p_description FROM codes " \
                            "WHERE p_section = %s AND p_store = %s AND p_status = %s"
                self.cursor.execute(sql_query, (p_section, p_store, 1))
            else:
                sql_query = "SELECT p_id, p_code, p_description FROM codes " \
                            "WHERE p_section = %s AND p_store = %s AND p_date = %s AND p_status = %s"
                self.cursor.execute(sql_query, (p_section, p_store, p_date, 1))
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            return f"Ошибка при фильтрации записей: {e}"

        finally:
            self.close_connection()

    # удаление записей
    def delete_records(self, p_id):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных
        try:
            sql_query = "DELETE FROM codes WHERE p_id = %s"
            self.cursor.execute(sql_query, (p_id,))
            self.connection.commit()
            return "Запись удалена."
        except Exception as e:
            return f"Ошибка при удалении записи: {e}"

        finally:
            self.close_connection()

    # изменение записей
    def update_records(self, p_id, ch_object, changes):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных

        try:
            sql_query = f"UPDATE codes SET p_{ch_object} = %s WHERE p_id = %s"
            self.cursor.execute(sql_query, (changes, p_id))
            self.connection.commit()
            return "Запись изменена."
        except Exception as e:
            return f"Ошибка при изменении записи: {e}"

        finally:
            self.close_connection()

    # получаем список разделов
    def get_section(self):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных
        try:
            sql_query = "SELECT p_section FROM codes"
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            result_list = [item[0] for item in results]
            return result_list

        finally:
            self.close_connection()

    # получаем список магазинов для раздела
    def get_store(self, p_section):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных
        try:
            sql_query = "SELECT p_store FROM codes WHERE p_section = %s"
            self.cursor.execute(sql_query, (p_section,))
            results = self.cursor.fetchall()
            result_list = [item[0] for item in results]
            return result_list

        finally:
            self.close_connection()

    # получаем полный список магазинов
    def get_all_stores(self):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных
        try:
            sql_query = "SELECT p_store FROM codes"
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            result_list = [item[0] for item in results]
            return result_list

        finally:
            self.close_connection()

    # получаем список промокодов
    def get_codes(self, p_store):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных
        try:
            sql_query = "SELECT p_code, p_description, p_date FROM codes WHERE p_store = %s AND p_status = %s"
            self.cursor.execute(sql_query, (p_store, 1))
            results = self.cursor.fetchall()
            return results

        finally:
            self.close_connection()

    # получаем список ID всех пользователей
    def search_user_ids(self):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных
        query = f"SELECT u_id FROM profile"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        self.close_connection()
        return results

    # изменение баннеров
    def update_banners(self, b_imgID, b_for):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных

        try:
            sql_query = f"UPDATE banners SET b_imgID = %s WHERE b_for = %s"
            self.cursor.execute(sql_query, (b_imgID, b_for))
            self.connection.commit()
            return f"Добавлен баннер для <b>{b_for}</b>"
        except Exception as e:
            return f"Ошибка при добавлении баннера: {e}"

        finally:
            self.close_connection()

    # получаем список ID баннера
    def search_banner_id(self, b_for):
        self._init_db()  # Передаем параметры подключения
        self.connect_to_database()  # Подключаемся к базе данных
        query = f"SELECT b_imgID FROM banners WHERE b_for = %s"
        self.cursor.execute(query, (b_for,))
        result = self.cursor.fetchone()
        self.close_connection()
        return result
