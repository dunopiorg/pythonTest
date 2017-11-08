import socket
import threading

class serverTcp():
    __host = None
    __port = None
    __server_socket = None
    __recvqueue = None
    __client_socket = []

    def __init__(self, host, port, recvqueue):
        self.__host = host
        self.__port = port
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((self.__host, self.__port))
        self.__server_socket.listen(5)
        self.__recvqueue = recvqueue

    def recv(self):
        try:
            print('[Waiting for the connection...]')
            client_socket, addr = self.__server_socket.accept()
            t = threading.Thread(target=self.open)
            t.start()
            self.__client_socket.append({'socket':client_socket, 'address':addr})

            while True:
                print('[Waiting for Responce...]')
                data = client_socket.recv(1024).decode('utf-8')
                print(data)
                self.__recvqueue.put(data)
        except Exception as e:
            print(e.args)
            self.__server_socket.close()
        finally:
            self.__server_socket.close()

    def sender(self, sendmsg):
        self.__client_socket[0]['socket'].send(sendmsg.encode('utf-8'))

    def open(self):
        self.recv()

    def close(self):
        self.__server_socket.close()

class clientTcp():
    __host = None
    __port = None
    __client_socket = None

    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connector(self):
        self.__client_socket.connect((self.__host, self.__port))
        print('Connected to ', self.__host)

    def sender(self, msg):
        self.__client_socket.send(msg.encode('utf-8'))

    def recv(self):
        while True:
            print((self.__client_socket.recv(1024)).decode('utf-8'))