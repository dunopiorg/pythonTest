import math

from lib import DBConnection as db


class StringAnalyser(object):
    __database = None
    __serverInfo = None
    __userId = None
    __pw = None

    def __init__(self):
        self.__database = "BASEBALL"
        self.__serverInfo = '211.115.88.17'
        self.__userId = 'LAB'
        self.__pw = 'tmvhcm@ilAb10@$'

    def dbConnector(self, dict_option):
        conn = db.MSSqlConnector(server=self.__serverInfo
                                   , user=self.__userId
                                   , password=self.__pw
                                   , database=self.__database)
        conn.open(dict_option=dict_option)
        return conn

    def runRecord(self, dbConn, data):
        byten=[10, 100, 1000]
        inputs = data.split()
        runString = ['홈인', '홈런']
        runHow = [text for text in runString if text in inputs]
        name = None
        result = None
        if len(runHow) > 0:
            if runHow[0] == runString[0]:
                name = inputs[2]
            else:
                name = inputs[1]

            query = "SELECT [NAME]"\
                           "               ,[PCODE]"\
                           "               ,SUM([RUN])"\
                           "  FROM [BASEBALL].[dbo].[Hitter] "\
                           "WHERE GDAY LIKE '2017%' "\
                           "      AND NAME = %s "\
                           "GROUP BY [NAME],[PCODE]"

            items = dbConn.select(query, name)

            totalRun = int(items[0][2])

            roundRun = int(math.ceil(totalRun / 10) * 10)

            """if roundRun in byten:
                result = "%s 선수 곧 %d 득점을 앞에 두고 있습니다. " % (name, roundRun)"""
            result = "%s 선수 지금까지 %d 득점을 했는데요, %d점까지 %d점 남았습니다. " % (name, totalRun + 1, roundRun, roundRun - (totalRun + 1) )

            return result
        else:
            return ""


