import queue
import time
import socket
import threading

from lib import tcpSocket
from lib import gameHelper

# Message Queue 생성
recv_broadcast_queue = queue.Queue()

# Program Start
"""
if __name__ == "__main__":
    server = tcpSocket.serverTcp(socket.gethostname(), 12222, recv_broadcast_queue)
    analyser = classifier.StringAnalyser()
    conn = analyser.dbConnector(False)

    try:
        thread1 = threading.Thread(target=server.open)
        thread1.start()
        print('[thread1 Started] socket server')

        while True:
            if recv_broadcast_queue.qsize() > 0:

                result = analyser.runRecord(conn, recv_broadcast_queue.get())
                if result is not None and len(result) > 0:
                    server.sender("캐스터: " + result)

    except Exception as e:
        server.close()
"""

if __name__ == "__main__":

    """
    server = tcpSocket.serverTcp(socket.gethostname(), 12222, recv_broadcast_queue)
    
    try:
        
        thread1 = threading.Thread(target=server.open)
        thread1.start()
        print('[thread1 Started] socket server')
        
    except Exception as e:
        server.close()
    """

    currInfoDict = None
    prevInfoDict = None
    gmHelper = gameHelper.GameHelper()
    currInfoDict = gmHelper.get_live_data()
    caster_thread = threading.Thread(target=gmHelper.get_queue)
    caster_thread.start()
    # Test Start ------------------------------------
    testTuple = gmHelper.test_live_data('20170912OBNC0')
    for i, testDict in enumerate(testTuple):
        print("문자: " + testDict['LiveText'])
        gmHelper.currRowNum = i
        result = gmHelper.get_what_info(testDict['LiveText'])

        if result:
            gmHelper.make_sentence(result)
        time.sleep(1)

    # Test End -------------------------------------
    prevInfoDict = currInfoDict


