import queue
import time
import socket
import threading

from pymysql.connections import MysqlPacket
from lib import classifier, tcpSocket

from lib import gameHelper as gh

# Message Queue 생성
__recvBroadCastQ = queue.Queue()

# Program Start
"""
if __name__ == "__main__":
    server = tcpSocket.serverTcp(socket.gethostname(), 12222, __recvBroadCastQ)
    analyser = classifier.StringAnalyser()
    conn = analyser.dbConnector(False)

    try:
        thread1 = threading.Thread(target=server.open)
        thread1.start()
        print('[thread1 Started] socket server')

        while True:
            if __recvBroadCastQ.qsize() > 0:

                result = analyser.runRecord(conn, __recvBroadCastQ.get())
                if result is not None and len(result) > 0:
                    server.sender("캐스터: " + result)

    except Exception as e:
        server.close()
"""

if __name__ == "__main__":
    server = tcpSocket.serverTcp(socket.gethostname(), 12222, __recvBroadCastQ)

    try:
        thread1 = threading.Thread(target=server.open)
        thread1.start()
        print('[thread1 Started] socket server')

    except Exception as e:
        server.close()

    currInfoDict = None
    prevInfoDict = None
    gmHelper = gh.GameHelper()
    currInfoDict = gmHelper.getLiveData()

    # Test Start ------------------------------------
    testTuple = gmHelper.testLiveData()
    for i, testDict in enumerate(testTuple):
        print(testDict['LiveText'])
        gmHelper.currRowNum = i
        gmHelper.getHowInfo(testDict['HOW'])
        time.sleep(1)

    # Test End -------------------------------------
    """
    if currInfoDict['HOW'] in ['BH', 'HR']:
        gmHelper.getHowInfo(currInfoDict['HOW'])
        print('Home Run')
    """
    prevInfoDict = currInfoDict


