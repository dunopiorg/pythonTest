import queue
import time
import socket
import threading

from lib import tcpSocket
from lib import game_app

# Message Queue 생성
# recv_broadcast_queue = queue.Queue()

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
    game_id = '20170926HHLT0'  # 20170912OBNC0
    sleep_second = 1
    gm_app = game_app.GameApp(game_id)

    msg_thread = threading.Thread(target=gm_app.message_thread, name='Message Thread')
    msg_thread.start()
    caster_thread = threading.Thread(target=gm_app.score_thread, name='Score Table Thread')
    caster_thread.start()
    # Test Start ------------------------------------
    game_live_tuple = gm_app.test_live_data(game_id)
    for game_live_dict in game_live_tuple:
        print("문자: " + game_live_dict['LiveText'])
        result = gm_app.get_what_info(game_live_dict)

        if result:
            gm_app.make_sentence(result)
        time.sleep(sleep_second)

    # Test End -------------------------------------
