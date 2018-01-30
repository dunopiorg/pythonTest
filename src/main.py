import queue
import time
import socket
import threading

from lib import tcpSocket
from lib import game_helper

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
    game_id = '20170912OBNC0'  # 20170926HHLT0
    sleep_second = 0.1
    currInfoDict = None
    prevInfoDict = None
    gm_helper = game_helper.GameHelper()
    currInfoDict = gm_helper.get_live_data()
    caster_thread = threading.Thread(target=gm_helper.get_queue)
    caster_thread.start()
    # Test Start ------------------------------------
    testTuple = gm_helper.test_live_data(game_id)
    for i, testDict in enumerate(testTuple):
        print("문자: " + testDict['LiveText'])
        gm_helper.curr_row_num = i
        result = gm_helper.get_what_info(testDict)

        if result:
            gm_helper.make_sentence(result)
        time.sleep(sleep_second)

    # Test End -------------------------------------
    prevInfoDict = currInfoDict
