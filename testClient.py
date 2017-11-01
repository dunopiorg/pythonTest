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
dbConn = db.MSSqlConnector(server=serverInfo, user=userId, password=pw, database=database)
dbConn.open(asDict=True)

# Query 설정
query =  'SELECT [gameID]'\
                '      ,[GYEAR]'\
                '      ,[seqNO]'\
                '      ,[inning]'\
                '      ,[bTop]'\
                '      ,[ballcount]'\
                '      ,[ball_type]'\
                '      ,[strike]'\
                '      ,[ball]'\
                '      ,[out]'\
                '      ,[pitcher]'\
                '      ,[batter]'\
                '      ,[A_Score]'\
                '      ,[H_Score]'\
                '      ,[A_Run]'\
                '      ,[H_Run]'\
                '      ,[LiveText]'\
                '  FROM [BASEBALL_NEW].[dbo].[IE_LiveText_Score_MIX]'\
                '  WHERE gameID = %s'\
                '  ORDER BY gameID'

# Data Selection
items = dbConn.select(query, '77771030HTOB0')
count = items.__len__()
arr = np.array(items)

# TCP Client 생성
client_server = tcpSocket.clientTcp(socket.gethostname(), 12222)
client_server.connector()

# Thread로 Message Receiver 생성
thread_recv =threading.Thread(target=client_server.recv)
thread_recv.start()
print('[thread_recv Started] client receiver ')

testItems = ["3루주자 버나디나 : 홈인"
    , "2루주자 최형우 : 홈인"
    , "1루주자 나지완 : 홈인"
    , "이범호 : 좌익수 뒤 홈런 (홈런거리:115M) "]

for i in testItems: # range(count):
    #client_server.sender(items[i]['LiveText'])
    msg = "문자: " + i
    print(msg)
    client_server.sender(msg)
    time.sleep(5)

