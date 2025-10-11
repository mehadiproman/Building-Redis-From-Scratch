import socket
import threading

class TCPServer:
    def __init__(self, host='localhost', port=6379):
        # Create a TCP/IPv4 socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"Server listening on {host}:{port}")

        # In-memory key-value store
        self.store = {}
        # Lock for thread-safe access to the store
        self.lock = threading.Lock()

    def handle_client(self, conn, addr):
        print(f"Connected by {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break  # client closed connection

                message = data.decode(errors='ignore').strip()
                if not message:
                    continue  # ignore empty lines

                print(f"Received from {addr}: {message}")

                # Split command and arguments
                parts = message.split()
                command = parts[0].upper()

                if command == "PING":
                    conn.sendall(b"+PONG\r\n")

                elif command == "ECHO":
                    response = " ".join(parts[1:]) if len(parts) > 1 else ""
                    conn.sendall(b"+" + response.encode() + b"\r\n")

                elif command == "SET":
                    if len(parts) >= 3:
                        key = parts[1]
                        value = " ".join(parts[2:])
                        with self.lock:
                            self.store[key] = value
                        conn.sendall(b"+OK\r\n")
                    else:
                        conn.sendall(b"-ERR SET requires key and value\r\n")

                elif command == "GET":
                    if len(parts) >= 2:
                        key = parts[1]
                        with self.lock:
                            value = self.store.get(key)
                        if value is not None:
                            conn.sendall(b"+" + value.encode() + b"\r\n")
                        else:
                            conn.sendall(b"$-1\r\n")  # Redis-like nil
                    else:
                        conn.sendall(b"-ERR GET requires key\r\n")

                elif command == "DEL":
                    if len(parts) >= 2:
                        key = parts[1]
                        with self.lock:
                            if key in self.store:
                                del self.store[key]
                                conn.sendall(b"+OK\r\n")
                            else:
                                conn.sendall(b"$-1\r\n")
                    else:
                        conn.sendall(b"-ERR DEL requires key\r\n")

                elif command == "QUIT":
                    conn.sendall(b"+OK Goodbye\r\n")
                    break

                else:
                    conn.sendall(b"-ERR Unknown command\r\n")

        except Exception as e:
            # Only log exceptions; do NOT send to closed socket
            print(f"Error with {addr}: {e}")
        finally:
            conn.close()
            print(f"Disconnected {addr}")

    def run(self):
        try:
            while True:
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.server_socket.close()


if __name__ == "__main__":
    server = TCPServer()
    server.run()