import pymssql

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
