from lib import DBConnection as db, tcpSocket

# DB Setting
baseball_new = "BASEBALL_NEW"
baseball = "BASEBALL"
serverInfo = '211.115.88.19'
userId = 'LAB'
pw = 'tmvhcm@ilAb10@$'


def getLiveText(game_Id=None):
    try:
        # DB 연결
        ms_conn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=baseball_new)
        ms_conn.open(dict_option=False)

        my_conn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        ms_query = "SELECT *" \
                  "  FROM [BASEBALL_NEW].[dbo].[IE_LiveText_Score_MIX] where gyear = 2017 "

        my_query = "INSERT INTO baseball.ie_livetext_score_mix " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s," \
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s," \
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s," \
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # MS Data Selection
        ms_items = ms_conn.select(ms_query, game_Id)
        count = ms_items.__len__()

        row_count = 0
        for i in range(count):
            # Insert to MySql DB
            my_conn.insert(my_query, ms_items[i])
            row_count += 1
            print(row_count)
    finally:
        ms_conn.close()

def getGameContApp(gmkey=None):
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=baseball_new)
        dbMsConn.open(dict_option=False)

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
        dbMsConn.open(dict_option=False)

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
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = "SELECT * " \
                  "FROM [{0}].[dbo].[Hitter] " \
                  "WHERE GDAY like '2000%'".format(baseball_all)

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
    baseball_all = "BASEBALL"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=baseball_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = "SELECT GMKEY,SUBSTRING(GDAY, 0, 5) AS GYEAR, GDAY,TURN,NAME,PCODE,TEAM,POSI,CHIN,CHTURN,CHBCNT,CHIN2 " \
                  "FROM [BASEBALL].[dbo].[Entry] where GDAY < 20170101"

        myQuery = "INSERT INTO baseball.entry " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, '')
        count = msItems.__len__()

        insert_count = 0
        for i in range(count):
            # Insert to MySql DB
            insert_count += dbMyConn.insert(myQuery, msItems[i])
            print(insert_count)

    finally:
        dbMsConn.close()

def get_ie_batterrecord():
    baseball_all = "BASEBALL_NEW"
    serverInfo_all = '211.115.88.19'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=baseball_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = "SELECT * " \
                  "FROM [BASEBALL_NEW].[dbo].[IE_BatterRecord] where gameid != '20170912OBNC0'"

        myQuery = "INSERT INTO baseball.ie_batterrecord " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s, %s,%s, 0,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, '')
        count = msItems.__len__()

        insert_count = 0
        for i in range(count):
            # Insert to MySql DB
            insert_count += dbMyConn.insert(myQuery, msItems[i])
            print(insert_count)

    finally:
        dbMsConn.close()

def get_ie_pitcherrecord():
    baseball_all = "BASEBALL_NEW"
    serverInfo_all = '211.115.88.19'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all,
                                     database=baseball_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = "SELECT * " \
                  "FROM [BASEBALL_NEW].[dbo].[IE_PitcherRecord]"

        myQuery = "INSERT INTO baseball.ie_pitcherrecord " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, 0,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, '')
        count = msItems.__len__()

        insert_count = 0
        for i in range(count):
            # Insert to MySql DB
            insert_count += dbMyConn.insert(myQuery, msItems[i])
            print(insert_count)

    finally:
        dbMsConn.close()

def get_pitchrecord_2011():
    baseball_all = "PTS"
    serverInfo_all = '211.115.88.19'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'
    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all,
                                     database=baseball_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = "SELECT * " \
                  "FROM [PTS].[dbo].[PITCHRECORD_2011] where gyear = 2017"

        myQuery = "INSERT INTO baseball.pitchrecord_2011 " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                  "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                  "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                  "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, '')
        count = msItems.__len__()

        insert_count = 0
        for i in range(count):
            # Insert to MySql DB
            insert_count += dbMyConn.insert(myQuery, msItems[i])
            print(insert_count)

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
        dbMsConn.open(dict_option=False)

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
        dbMsConn.open(dict_option=False)

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

def get_gameinfo_all(gmkey=None):
    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  '  FROM [BASEBALL].[dbo].[Gameinfo]'

        myQuery = "INSERT INTO baseball.gameinfo " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery, gmkey)
        count = msItems.__len__()

        result_cnt = 0
        for i in range(count):
            # Insert to MySql DB
            result = dbMyConn.insert(myQuery, msItems[i])
            result_cnt += result
            print(result_cnt)
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
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [BASEBALL_NEW].[dbo].[KBO_PitZone] WHERE GYEAR = '2016'"

        myQuery = "INSERT INTO baseball.kbo_pitzone " \
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

def get_person():
    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [BASEBALL].[dbo].[Person] "

        myQuery = "INSERT INTO baseball.person " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery)
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
            print('Success Count : ', result)
    finally:
        dbMsConn.close

def get_battotal():
    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [BASEBALL].[dbo].[BatTotal] "

        myQuery = "INSERT INTO baseball.battotal VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery)
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
            print('Success Count : ', result)
    finally:
        dbMsConn.close

def get_pittotal():
    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [BASEBALL].[dbo].[PitTotal] "

        myQuery = "INSERT INTO baseball.pittotal " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery)
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
            print('Success Count : ', result)
    finally:
        dbMsConn.close

def get_pitcher():
    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [BASEBALL].[dbo].[Pitcher] "

        myQuery = "INSERT INTO baseball.pitcher " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, " \
                  "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, " \
                  "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, " \
                  "%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery)
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
            print('Success Count : ', result)
    finally:
        dbMsConn.close

def get_record_matrix_mix():
    database_all = "BASEBALL_NEW"
    serverInfo_all = '211.115.88.19'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [BASEBALL_NEW].[dbo].[IE_RECORD_MATRIX_MIX] "

        myQuery = "INSERT INTO baseball.record_matrix_mix " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery)
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
            print('Success Count : ', result)
    finally:
        dbMsConn.close

def get_teamrank():
    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.19'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'
    table_name = 'TeamRank'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [%s].[dbo].[%s] where gyear = '2016'" % (database_all, table_name)

        myQuery = "INSERT INTO baseball.teamrank " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery)
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
            print('Success Count : ', result)
    finally:
        dbMsConn.close

def get_teamrank_all():
    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.17'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'
    table_name = 'TeamRank'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [%s].[dbo].[%s]" % (database_all, table_name)

        myQuery = "INSERT INTO baseball.teamrank " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery)
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
            print('Success Count : ', result)
    finally:
        dbMsConn.close

def get_teamrank_daily():
    database_all = "BASEBALL"
    serverInfo_all = '211.115.88.19'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'
    table_name = 'TeamRank_daily'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('localhost', 3307, 'root', 'lab2ai64', 'baseball')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [%s].[dbo].[%s] where gyear != '2017'" % (database_all, table_name)

        myQuery = "INSERT INTO baseball.teamrank_daily " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        # MS Data Selection
        msItems = dbMsConn.select(msQuery)
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
            print('Success Count : ', result)
    finally:
        dbMsConn.close

def set_entryt_aws():
    database_all = "MINOR_BASEBALL"
    serverInfo_all = '211.115.88.19'
    userId_all = 'LAB'
    pw_all = 'tmvhcm@ilAb10@$'
    table_name = 'Entry'

    try:
        # DB 연결
        dbMsConn = db.MSSqlConnector(server=serverInfo_all, user=userId_all, password=pw_all, database=database_all)
        dbMsConn.open(dict_option=False)

        dbMyConn = db.MySqlConnector('myrds.cqqe2lakgloq.ap-northeast-2.rds.amazonaws.com', 3306, 'lab2ai', 'lab2ailab2ai', 'baseball_futures')

        # Query 설정
        msQuery = 'SELECT *' \
                  "  FROM [%s].[dbo].[%s]" % (database_all, table_name)

        myQuery = "INSERT INTO baseball_futures.Entry " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # MS Data Selection
        msItems = dbMsConn.select(msQuery)
        count = msItems.__len__()

        result = 0
        for i in range(count):
            # Insert to MySql DB
            result += dbMyConn.insert(myQuery, msItems[i])
            print('Success Count : ', result)
    finally:
        dbMsConn.close

if __name__ == "__main__":
    # get_person()
    # getLiveText()
    # get_teamrank_all()
    # get_gameinfo_all()
    # get_battotal()
    # getGameContApp('20170926HHLT0')
    # getGameContApp()
    # getGameContApp_all()
    # getHitter()
    # getEntry()
    # get_ie_batterrecord()
    # get_ie_pitcherrecord()
    get_pitchrecord_2011()
    # getKbo_rank10_basic()
    # get_gameinfo()
    # get_pitzone()
    # get_pittotal()
    # get_pitcher()
    # get_record_matrix_mix()
    # get_teamrank_daily()
    # get_teamrank()
    # set_entryt_aws()

    pass
