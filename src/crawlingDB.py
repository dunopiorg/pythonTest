from lib import DBConnection as db, tcpSocket

# DB Setting
database = "BASEBALL_NEW"
serverInfo = '211.115.88.19'
userId='LAB'
pw='tmvhcm@ilAb10@$'

def getLiveText(gameId):
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=database)
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
        dbMsConn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=database)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  '  FROM [BASEBALL_NEW].[dbo].[GameContApp]' \
                  '  WHERE GMKEY = %s' \
                  '  ORDER BY SERNO'
        msQuery = 'SELECT *' \
                  '  FROM [BASEBALL_NEW].[dbo].[GameContApp]' \
                  '  WHERE GYEAR = 2017'

        # TODO : value 입력
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

def getHitter():
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=database)
        dbMsConn.open(asDict=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = "SELECT * " \
                  "FROM [BASEBALL_NEW].[dbo].[Hitter] " \
                  "WHERE GDAY LIKE '2017%' "

        # TODO : value 입력
        myQuery = "INSERT INTO baseball.hitter " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, '')
        count = msItems.__len__()

        for i in range(count):
            # Insert to MySql DB
            dbMyConn.insert(myQuery, msItems[i])

    finally:
        dbMsConn.close()

def getEntry():
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=database)
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

if __name__ == "__main__":
    # getLiveText('20170912OBNC0')
    # getGameContApp('20170912OBNC0')
    #getGameContApp()
    # getHitter()
    getEntry()