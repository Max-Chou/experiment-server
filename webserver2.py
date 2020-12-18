import io
import socket
import sys
from datetime import datetime

class WSGIServer():
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    # this server can only handle 1 request
    request_queue_size = 1

    def __init__(self, server_address, server_port=80):
        # Create a listening socket
        self.listen_socket = socket.socket(
            WSGIServer.address_family,
            WSGIServer.socket_type,
        )

        self.listen_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.listen_socket.bind((server_address, server_port))
        self.listen_socket.listen(self.request_queue_size)

        # server hostname, server address, server port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_address = server_address
        self.server_port = port

        # response headers
        self.headers_set = []


    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        """The server makes connections when receiving requests from clients.
        After processing request and closing the connection, the server wait for another client.
        """
        while True:
            self.client_connection, self.client_address = self.listen_socket.accept()
            # handle one request and close connection
            self.handle_one_request()

    def handle_one_request(self):
        """The function handles requests from client. Basically, the function 
        send the requests and headers to the WSGI application before closing the
        connection.
        """
        request_data = self.client_connection.recv(1024)
        self.request_data = request_data.decode('utf-8')

        print(''.join(
            f'< {line}\n' for line in self.request_data.splitlines()
        ))

        # parse request data
        request_line = self.request_data.splitlines()[0]
        request_line = request_line.rstrip('\r\n')
        (
            self.request_method,
            self.path,
            self.request_version
        ) = request_line.split()

        # send request to the WSGI application
        result = self.application(self.environ, self.start_response)


        # make response 
        self.finish_response(result)
        
    @property
    def environ(self):
        """The environment variables for WSGI applications.
        """
        env = {}

        # WSGI variables
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = io.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False

        # CGI variables
        env['REQUEST_METHOD'] = self.request_method # GET, POST...
        env['PATH_INFO'] = self.path                # /hello
        env['SERVER_NAME'] = self.server_name       # localhost
        env['SERVER_PORT'] = str(self.server_port)  # 8888

        return env

    def start_response(self, status, response_headers, exc_info=None):
        """The function adds additional headers.
        """
        now = datetime.now()

        server_headers = [
            ('Date', now.strftime("%A, %d %B %Y %H:%M:%S %Z")),
            ('Server', 'WSGIServer 0.1')
        ]
        self.headers_set = [status, response_headers + server_headers]

    def finish_response(self, result):
        """Send the response to client.
        """
        try:
            status, response_headers = self.headers_set
            response = f"HTTP/1.1 {status}\r\n"
            for header in response_headers:
                response += "{0}: {1}\r\n".format(*header)
            
            response += '\r\n'
            for data in result:
                response += data.decode('utf-8')
            
            print(''.join(
                f'> {line}\n' for line in response.splitlines()
            ))

            response_bytes = response.encode()
            self.client_connection.sendall(response_bytes)
        finally:
            self.client_connection.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    
    app_path = sys.argv[1]

    # get application
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    
    # create server
    host = 'localhost'
    port = 8888
    server = WSGIServer(host, port)
    server.set_app(application)
    print(f"WSGIServer: Serving HTTP on {host}:{port} ...\n")
    server.serve_forever()
