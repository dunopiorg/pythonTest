import pymssql
import pymysql.cursors


class MSSqlConnector(object):
    __server = None
    __user = None
    __password = None
    __database = None
    __connection = None
    __session = None

    def __init__(self, server, user, password, database):
        self.__server = server
        self.__user = user
        self.__password = password
        self.__database = database

    def open(self, dict_option=True):
        try:
            conn = pymssql.connect(server=self.__server, user=self.__user, password=self.__password,
                                   database=self.__database, charset='utf8')
            self.__connection = conn
            self.__session = conn.cursor(as_dict=dict_option)
        except Exception as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))

    def close(self):
        self.__connection.close()

    def select(self, query, *args):
        result = []
        try:
            self.__session.execute(query, args)
            result = [item for item in self.__session.fetchall()]
        except Exception as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            self.__connection.close()

        return result


class MySqlConnector(object):
    __host = None
    __user = None
    __password = None
    __db = None

    def __init__(self, host, port, user, pw, db):
        self.__host = host
        self.__user = user
        self.__password = pw
        self.__db = db
        self.__port = port

    def select(self, query, use_dict=False, *args):
        option = pymysql.cursors.DictCursor if use_dict is True else None
        conn = pymysql.connect(host=self.__host, port=self.__port, user=self.__user, password=self.__password,
                               db=self.__db, charset='utf8mb4')
        try:
            with conn.cursor(option) as cursor:
                if args.__len__() > 0:
                    cursor.execute(query, args)
                else:
                    cursor.execute(query)
                result = cursor.fetchall()

            return result
        finally:
            conn.close()

    def insert(self, query, args):
        conn = pymysql.connect(host=self.__host, port=self.__port, user=self.__user, password=self.__password,
                               db=self.__db, charset='utf8mb4')
        try:
            with conn.cursor() as cursor:
                result = cursor.execute(query, args)
                conn.commit()

            return result
        finally:
            conn.close()
