import socket
import select
import errno

class RedisLikeServer:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        self.running = True

        self.client_sockets = set()
        self.client_buffers = {}
        self.client_addresses = {}
        self.store = {}

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setblocking(False)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(128)

        print(f"Single-threaded Redis-like server listening on {self.host}:{self.port}")
        self._event_loop()

    def _event_loop(self):
        while self.running:
            readable = [self.server_socket] + list(self.client_sockets)
            writeable = []
            errors = list(self.client_sockets)

            ready_read, ready_write, error_sockets = select.select(readable, writeable, errors, 1.0)

            if self.server_socket in ready_read:
                self._accept_new_connection()
            
            for client_socket in ready_read:
                if client_socket != self.server_socket:
                    self._handle_client_data(client_socket)
            
            for sock in error_sockets:
                self._disconnect_client(sock)

    def _accept_new_connection(self):
        try:
            client_socket, address = self.server_socket.accept()
            client_socket.setblocking(False)

            self.client_sockets.add(client_socket)
            self.client_buffers[client_socket] = ""
            self.client_addresses[client_socket] = address
            
            print(f"New connection from {address}")
            self._send_to_client(client_socket, "+OK Redis-like server ready\r\n")
        
        except socket.error:
            pass
    
    def _handle_client_data(self, client_socket):
        try:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                self._disconnect_client(client_socket)
                return
            
            self.client_buffers[client_socket] += data
            self._process_client_buffer(client_socket)

        except socket.error as e:
            if e.errno != errno.EWOULDBLOCK:
                self._disconnect_client(client_socket)

    def _process_client_buffer(self, client_socket):
        buffer = self.client_buffers[client_socket].replace('\r\n', '\n')

        while '\n' in buffer:
            line, buffer = buffer.split('\n',1)
            message = line.strip()

            if not message:
                continue

            self._execute_command(client_socket, message)

        self.client_buffers[client_socket] = buffer

    def _execute_command(self, client_socket, message):
        parts = message.split()
        command = parts[0].upper()

        if command == "PING":
            self._send_to_client(client_socket, "+PONG\r\n")

        elif command == "ECHO":
            response = " ".join(parts[1:]) if len(parts) > 1 else ""
            self._send_to_client(client_socket, f"+{response}\r\n")

        elif command == "SET":
            if len(parts) >= 3:
                key = parts[1]
                value = " ".join(parts[2:])
                self.store[key] = value
                self._send_to_client(client_socket, "+OK\r\n")
            else:
                self._send_to_client(client_socket, "-ERR SET requires key and value\r\n")

        elif command == "GET":
            if len(parts) >= 2:
                key = parts[1]
                value = self.store.get(key)
                if value is not None:
                    self._send_to_client(client_socket, f"+{value}\r\n")
                else:
                    self._send_to_client(client_socket, "$-1\r\n")
            else:
                self._send_to_client(client_socket, "-ERR GET requires key\r\n")

        elif command == "DEL":
            if len(parts) >= 2:
                key = parts[1]
                if key in self.store:
                    del self.store[key]
                    self._send_to_client(client_socket, "+OK\r\n")
                else:
                    self._send_to_client(client_socket, "$-1\r\n")
            else:
                self._send_to_client(client_socket, "-ERR DEL requires key\r\n")

        elif command == "QUIT":
            self._send_to_client(client_socket, "+OK Goodbye\r\n")
            self._disconnect_client(client_socket)

        else:
            self._send_to_client(client_socket, "-ERR unknown command\r\n")

    def _send_to_client(self, client_socket, message):
        try:
            client_socket.sendall(message.encode())
        except socket.error:
            self._disconnect_client(client_socket)

    def _disconnect_client(self, client_socket):
        address = self.client_addresses.get(client_socket, "Unknown")
        print(f"Disconnected {address}")

        if client_socket in self.client_sockets:
            self.client_sockets.remove(client_socket)

        self.client_buffers.pop(client_socket, None)
        self.client_addresses.pop(client_socket, None)

        try:
            client_socket.close()
        except socket.error:
            pass

if __name__ == "__main__":
    server = RedisLikeServer()
    server.start()