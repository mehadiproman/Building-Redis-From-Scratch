import socket
import threading

class TCPServer:
    def __init__(self, host='localhost', port=6379):
        # Create a TCP/IPv4 socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"Server listening on {host}:{port}", flush=True)  # flush ensures immediate output

    def handle_client(self, conn, addr):
        print(f"Connected by {addr}", flush=True)
        buffer = ""  # Buffer to accumulate characters
        try:
            while True:
                data = conn.recv(1024).decode(errors='ignore')
                if not data:
                    break

                buffer += data  # accumulate characters
                while "\n" in buffer:  # process full lines only
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()  # remove whitespace and \r
                    if not line:
                        continue

                    if line.upper() == "PING":
                        conn.sendall(b"+PONG\r\n")
                    else:
                        conn.sendall(b"-ERR Unknown command\r\n")
        except Exception as e:
            print(f"Error with {addr}: {e}", flush=True)
        finally:
            conn.close()
            print(f"Disconnected {addr}", flush=True)

    def run(self):
        try:
            while True:
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            print("\nShutting down server...", flush=True)
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = TCPServer()
    server.run()