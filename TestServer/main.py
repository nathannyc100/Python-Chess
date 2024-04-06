import socket

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serverSocket.bind(('', 8880))
serverSocket.listen(5)
connection, (rIP, rPORT) = serverSocket.accept()

print(f"Connection: {rIP}, {rPORT}")