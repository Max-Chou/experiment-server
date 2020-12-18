import socket

HOST, PORT = '', 8888

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print(f"Serving HTTP on port {PORT} ...")
while True:
    client_connection, client_address = listen_socket.accept()
    request_data = client_connection.recv(1024)
    print(request_data.decode('utf-8'))

    client_connection.send(b"HTTP/1.1 200 OK\r\n")
    client_connection.send(b"Content-Type: text/html\r\n\r\n")
    client_connection.send(b"<h1>Hello, World!</h1>")
    client_connection.close()

listen_socket.close()