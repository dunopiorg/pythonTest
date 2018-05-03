import queue
import time
import socket
import threading
import config

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
    game_id = '20170914SKOB0'  # 20170609SSHH0  20170912OBNC0 20170926HHLT0
    sleep_second = config.SLEEP_TIME
    gm_app = game_app.GameApp(game_id)

    msg_thread = threading.Thread(target=gm_app.message_thread, name='Message Thread')
    msg_thread.start()
    
    caster_thread = threading.Thread(target=gm_app.score_thread, name='Score Table Thread')
    caster_thread.start()
    # Test Start ------------------------------------
    game_live_tuple = gm_app.test_live_data(game_id)
    gm_app.game_thread = 1
    for game_live_dict in game_live_tuple:
        result = gm_app.get_what_info(game_live_dict)

        if result:
            gm_app.make_sentence(result)
        time.sleep(sleep_second)
    
    gm_app.game_thread = 0
    print("caster_thread isAlive():", caster_thread.is_alive())
    print("msg_thread isAlive():", msg_thread.is_alive())
    # Test End -------------------------------------
