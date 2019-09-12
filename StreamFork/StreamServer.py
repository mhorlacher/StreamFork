import socket
import struct
import time
import logging

from threading import Thread
from queue import Queue

MAX_CLIENTS = 16
MAX_CLIENT_QSIZE = 600

HEADER_FORMAT = struct.Struct('!I')


class _ClientHandler(Thread):
    
    def __init__(self, sock, address, server):
        Thread.__init__(self, daemon = True)

        self.sock = sock
        self.address = address
        self.server = server # Reference to server

        self.queue = Queue() # Message queue

    def _send_item(self, item):
        """Send item to client. Blocks thread."""

        self.sock.sendall(HEADER_FORMAT.pack(len(item)))
        self.sock.sendall(item)
        
    def run(self):
        """Pop items from queue and sent to client."""

        while True:
            try:
                item = self.queue.get()
                self._send_item(item)
            except BrokenPipeError:
                self.server.delete_client(self.ident)
            except OSError:
                self.server.delete_client(self.ident)
            except:
                raise

class StreamServer(Thread):

    def __init__(self, address):
        Thread.__init__(self, daemon = True)

        self.address = address
        self._clients = dict()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Disconnect clients and remove client threads when leaving context."""

        for ident in self._clients.keys():
            self.delete_client(ident)

    def queue_item(self, item):
        """Push item to every client queue."""

        for ident, client in self._clients.items():
            if client.queue.qsize() >= MAX_CLIENT_QSIZE:
                logging.warning('Client %s due to maximum QSIZE' % str(client.address))
                self.delete_client(ident)
            client.queue.put(item)

    def get_qsizes(self):
        """Get list of client queue sizes."""

        return [client.queue.qsize() for _, client in self._clients.items()]

    def delete_client(self, ident):
        """Close client socket and delete client thread."""

        self._clients[ident].sock.close()
        logging.warning('Client %s disconnected' % str(self._clients[ident].address))
        del self._clients[ident] # Delete only client thread reference (garbage collection?)

    def run(self):
        """Listen for incomming client connections."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            sock.bind(self.address)
            sock.listen(4)

            logging.info('Listening at %s' % str(sock.getsockname()))

            while True:
                try:
                    client_sock, client_addr = sock.accept()
                    if len(self._clients) >= MAX_CLIENTS:
                        # Refuse connections once client limit reached
                        client_sock.close()
                        continue

                    client_sock.shutdown(socket.SHUT_RD)
                    client = _ClientHandler(client_sock, client_addr, self)

                    logging.info('Connection from client %s' % str(client_addr))

                    client.start()
                    self._clients[client.ident] = client
                except:
                    raise


if __name__ == '__main__':
    with StreamServer(('localhost', 1060)) as server:
        server.start() # Start server thread

        last_time = time.time()
        for item in range(1,1000):
            server.queue_item(str(item).encode('utf-8'))
            time.sleep(1)

            if time.time() - last_time > 10.0:
                print('Client queue sizes:', server.get_qsizes())
                last_time = time.time()




