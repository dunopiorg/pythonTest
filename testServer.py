import queue
import socket
import threading

from lib import classifier, tcpSocket

# Message Queue 생성
__recvQueue = queue.Queue()

# Program Start
if __name__ == "__main__":
    server = tcpSocket.serverTcp(socket.gethostname(), 12222, __recvQueue)
    analyser = classifier.StringAnalyser()
    conn = analyser.dbConnector(False)

    try:
        thread1 = threading.Thread(target=server.open)
        thread1.start()
        print('[thread1 Started] socket server')

        while True:
            if __recvQueue.qsize() > 0:
                result = analyser.runRecord(conn, __recvQueue.get())
                if result is not None:
                    server.sender("캐스터: " + result)

    except Exception as e:
        server.close()

