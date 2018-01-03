from lib import DBConnection as db, tcpSocket

# DB Setting
baseball_new = "BASEBALL_NEW"
baseball = "BASEBALL"
serverInfo = '211.115.88.19'
userId='LAB'
pw='tmvhcm@ilAb10@$'

def getLiveText(gameId):
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=baseball_new)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 'root', '0000', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  '  FROM [BASEBALL_NEW].[dbo].[IE_LiveText_Score_MIX]' \
                  '  WHERE gameID = %s' \
                  '  ORDER BY gameID'

        myQuery = "INSERT INTO baseball.livetext_score_mix " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s," \
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s," \
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s," \
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, gameId)
        count = msItems.__len__()

        for i in range(count):
            # Insert to MySql DB
            dbMyConn.insert(myQuery, msItems[i])
    finally:
        dbMsConn.close()

def getGameContApp(gmkey=None):
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=baseball_new)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  '  FROM [BASEBALL_NEW].[dbo].[GameContApp]' \
                  '  WHERE GMKEY = %s' \
                  '  ORDER BY SERNO'
        msQuery = 'SELECT *' \
                  '  FROM [BASEBALL_NEW].[dbo].[GameContApp]' \
                  '  WHERE GYEAR = 2016'

        myQuery = "INSERT INTO baseball.gamecontapp " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, gmkey)
        count = msItems.__len__()

        for i in range(count):
            # Insert to MySql DB
            dbMyConn.insert(myQuery, msItems[i])
    finally:
        dbMsConn.close()

def getGameContApp_all(gmkey=None):

    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  '  FROM [BASEBALL_NEW].[dbo].[GameContApp]' \
                  '  WHERE GMKEY = %s' \
                  '  ORDER BY SERNO'
        msQuery = "SELECT *" \
                  "  FROM [BASEBALL].[dbo].[GameContApp]" \
                  "  WHERE GYEAR BETWEEN 1982 AND 1996"

        myQuery = "INSERT INTO baseball.gamecontapp_all " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, gmkey)
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
            print(result)

    finally:
        dbMsConn.close()


def getHitter():
    baseball_all = "BASEBALL"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=baseball_all)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = "SELECT * " \
                  "FROM [{0}].[dbo].[Hitter] " \
                  "WHERE GDAY LIKE '2016%' ".format(baseball_all)

        myQuery = "INSERT INTO baseball.hitter " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, '')
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
        print(result)

    finally:
        dbMsConn.close()

def getEntry():
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=baseball_new)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = "SELECT * " \
                  "FROM [BASEBALL_NEW].[dbo].[Entry] "

        myQuery = "INSERT INTO baseball.entry " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, '')
        count = msItems.__len__()

        for i in range(count):
            # Insert to MySql DB
            dbMyConn.insert(myQuery, msItems[i])

    finally:
        dbMsConn.close()

def getKbo_rank10_basic(gmkey=None):

    database_all = "BBIS"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  '  FROM [BBIS].[dbo].[kbo_rank10_basic]'

        myQuery = "INSERT INTO baseball.kbo_rank10_basic " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, gmkey)
        count = msItems.__len__()

        for i in range(count):
            # Insert to MySql DB
            result = dbMyConn.insert(myQuery, msItems[i])
            print(result)
    finally:
        dbMsConn.close

def get_gameinfo(gmkey=None):
    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.19'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  '  FROM [BASEBALL].[dbo].[Gameinfo]'

        myQuery = "INSERT INTO baseball.gameinfo " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, gmkey)
        count = msItems.__len__()

        for i in range(count):
            # Insert to MySql DB
            result = dbMyConn.insert(myQuery, msItems[i])
            print(result)
    finally:
        dbMsConn.close

def get_pitzone(gmkey=None):
    database_all = "BASEBALL_NEW"
    serverInfo_all = '211.115.88.19'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [BASEBALL_NEW].[dbo].[KBO_PitZone] WHERE GYEAR = '2016'"

        myQuery = "INSERT INTO baseball.pitzone " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, gmkey)
        count = msItems.__len__()

        for i in range(count):
            # Insert to MySql DB
            result = dbMyConn.insert(myQuery, msItems[i])
            print(result)
    finally:
        dbMsConn.close

def get_pittotal(pitcher=None):
    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [BASEBALL].[dbo].[PitTotal] "

        myQuery = "INSERT INTO baseball.pittotal " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, gmkey)
        count = msItems.__len__()

        for i in range(count):
            # Insert to MySql DB
            result = dbMyConn.insert(myQuery, msItems[i])
            print(result)
    finally:
        dbMsConn.close

if __name__ == "__main__":
    # getLiveText('20170912OBNC0')
    # getGameContApp('20170912OBNC0')
    # getGameContApp()
    # getGameContApp_all()
    # getHitter()
    # getEntry()
    # getKbo_rank10_basic()
    # get_gameinfo()
    get_pitzone()