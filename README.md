# Build A Web Server in Python

References: [Build A Web Server From Scratch](https://ruslanspivak.com/lsbaws-part1/)

**Warning: you should use firefox as a client. It doesn't work well in Chrome.**

## Case 1 Simple Server

* Create Socket

* Bind and Listen on Port and Host

* Accept and make a connection (TCP Handshake)

* Client send request

* Server receive request

* Server send response

* Client receive response

* Connection Close


You can build the simple web server in any kind of programming language.

## Case 2 WSGI Web Server

WSGI Sever for Production

* gunicorn

* tornado


The simple server can only handle a request at a time.

## Case 3 Handle Many Requests at a time

### webserver3a

Can handle 5 clients but in sequence.

### webserver3b

Reviews

* Fork
* File Descriptor

The basic logic is that when the server accept a new connection from a client, the server fork a child to handle the request. The child don't accept a new connection, which is parent's job. After finishing the client's request, the child exits.

The problems

* Too many open files
    There is the max number of open files in Unix system. If you don't close the descriptors properly, the system will run out of available file descriptors.

* Zombie Process
    The parent process terminates before the child process exits. The child process becomes a zombie process.


### webserver3c

Reviews

* os.wait()

* signals

Add the event handler and wait for the child process terminates before the parent process terminates.

### webserver3d

The parent process was interrupted by the system calls. Using the exception to catch the error and restart the listening socket.

### webserver3e

The parent process receives too many *SIGCHLD* signals from child processes and misses some of them. The missed processes become zombies.