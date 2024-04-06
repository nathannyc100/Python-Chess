import socket
import ConnectionManager

#connectionManager = ConnectionManager.ConnectionManager()

#connectionManager.ConnectToServer('127.0.0.1', 8888)

connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connectionSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

ip = socket.gethostbyname('127.0.0.1')
connectionSocket.connect((ip, 8880))