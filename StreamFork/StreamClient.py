import socket
import struct
import logging

HEADER_FORMAT = struct.Struct('!I')

class StreamClient():

    def __init__(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.connect(address)
        self.sock.shutdown(socket.SHUT_WR)
        logging.info('Connected to %s' % str(self.sock.getpeername()))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.sock.close()

    def _recvall(self, size):
        data = b''
        while size:
            block = self.sock.recv(size)

            if not block:
                logging.error('Socket closed during message transmission')
                raise EOFError('Socket closed during message transmission')

            data += block
            size -= len(block)
        return data

    def __iter__(self):
        return self

    def __next__(self):
        try:
            (item_size,) = HEADER_FORMAT.unpack(self._recvall(HEADER_FORMAT.size))
            return self._recvall(item_size).decode('utf-8')
        except EOFError:
            raise StopIteration
        except:
            raise StopIteration


if __name__ == '__main__':
    with StreamClient(('localhost', 1060)) as stream:
        for item in stream:
            print(item)
