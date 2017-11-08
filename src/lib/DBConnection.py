import pymssql
import pymysql.cursors

class MSSqlConnector():

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

    def open(self, asDict=True):
        try:
            conn = pymssql.connect(server=self.__server, user=self.__user, password=self.__password, database=self.__database, charset='utf8')
            self.__connection = conn
            self.__session = conn.cursor(as_dict=asDict)
        except Exception as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))

    def close(self):
        self.__connection.close()

    def select(self, query, *args):

        try:
            self.__session.execute(query, args)
            result = [item for item in self.__session.fetchall()]
        except Exception as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            self.__connection.close()

        return result

class MySqlConnector():
    __host = None
    __user = None
    __password = None
    __db = None

    def __init__(self, host, user, pw, db):
        self.__host = host
        self.__user = user
        self.__password = pw
        self.__db = db

    def select(self, query, dict=False, *args):
        result = None
        option = pymysql.cursors.DictCursor if dict is True else None
        conn = pymysql.connect(host=self.__host, user=self.__user, password=self.__password, db=self.__db, charset='utf8mb4')
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

    """
    data = (
        ('홍진우', 1, '서울'),
        ('강지수', 2, '부산'),
        ('김청진', 1, '서울'),
    )
    sql = insert into customer(name,category,region)
             values (%s, %s, %s)
    curs.executemany(sql, data)
    conn.commit()
    복수개의 Insert
    """
    def insert(self, query, args):
        result = None

        try:
            conn = pymysql.connect(host=self.__host, user=self.__user, password=self.__password, db=self.__db, charset='utf8mb4')

            with conn.cursor() as cursor:
                result = cursor.execute(query, args)
                conn.commit()

            return result
        finally:
            conn.close()