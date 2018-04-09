import socket
import threading
import time

import numpy as np

from lib import DBConnection as db, tcpSocket

# DB Setting
database = "BASEBALL_NEW"
serverInfo = '211.115.88.19'
userId='LAB'
pw='tmvhcm@ilAb10@$'

# DB 연결
dbMsConn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=database)
dbMsConn.open(dict_option=False)

dbMyConn = db.MySqlConnector('localhost', 'root', '0000', 'baseball')

# Query 설정
msQuery =  'SELECT *'\
                '  FROM [BASEBALL_NEW].[dbo].[IE_LiveText_Score_MIX]'\
                '  WHERE gameID = %s'\
                '  ORDER BY gameID'

myQuery = "INSERT INTO baseball.ie_livetext_score_mix "\
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s,"\
          "%s, %s, %s, %s, %s, %s, %s, %s, %s,"\
          "%s, %s, %s, %s, %s, %s, %s, %s, %s,"\
          "%s, %s, %s, %s, %s, %s, %s, %s, %s)"

# MS Data Selection
msItems = dbMsConn.select(msQuery, '20170912OBNC0')
count = msItems.__len__()
arr = np.array(msItems)

# TCP Client 생성
client_server = tcpSocket.clientTcp(socket.gethostname(), 12222)
client_server.connector()

# Thread로 Message Receiver 생성
thread_recv =threading.Thread(target=client_server.recv)
thread_recv.start()
print('[thread_recv Started] client receiver ')

for i in range(count): #testItems:
    # MySql Data Insert
    # query = myQuery % msItems[i]
    mySqlInsert = dbMyConn.insert(myQuery, msItems[i])

    msg = "문자: " + msItems[i][31]
    print(msg)
    #client_server.sender(msg)
    time.sleep(1)

