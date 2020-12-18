import os
import signal
import socket
import time

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 5


def slayer(signum, frame):
    pid, status = os.wait()
    print(
        f'Child {pid} terminated with status {status}\n'
    )


def handle_request(client_connection):
    request = client_connection.recv(1024)

    # show the pid and ppid
    print(
        f'Child PID: {os.getpid()}. Parent PID: {os.getppid()}'
    )

    print(request.decode())
    http_response = b"""\
HTTP/1.1 200 OK

Hello, World!
"""
    client_connection.sendall(http_response)
    time.sleep(20)



def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print(f'Serving HTTP on {HOST}:{PORT} ...')
    print(f'Parent PID (PPID): {os.getpid()}\n')

    signal.signal(signal.SIGCHLD, slayer)

    while True:
        client_connection, client_address = listen_socket.accept()

        pid = os.fork()
        print(pid)
        if pid == 0:    # child
            listen_socket.close()   # close child's socket, child doesn't accept connections.
            handle_request(client_connection)
            client_connection.close()
            os._exit(0) # child exits here
        else:
            client_connection.close()   # close parent copy and loop over


if __name__ == '__main__':
    serve_forever()