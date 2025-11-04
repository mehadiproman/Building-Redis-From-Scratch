import socket  # Import the socket module for network connections
import threading  # Import the threading module for running tasks in parallel

class TCPServer:  # Defines the TCP server class
    def __init__(self, host='localhost', port=6379):  # Initializes the server with a host and port
        # Create a TCP/IPv4 socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creates a new TCP socket
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allows the reuse of the same address
        self.server_socket.bind((host, port))  # Binds the socket to the given host and port
        self.server_socket.listen(5)  # Listens for incoming connections, with a backlog of 5
        print(f"Server listening on {host}:{port}", flush=True)  # Prints a message that the server is running, flush ensures it's displayed immediately

    def handle_client(self, conn, addr):  # Method to handle a single client connection
        print(f"Connected by {addr}", flush=True)  # Prints the address of the connected client
        buffer = ""  # Initializes an empty buffer to store incoming data
        try:
            while True:  # Loop to continuously receive data from the client
                data = conn.recv(1024).decode(errors='ignore')  # Receives up to 1024 bytes and decodes it to a string
                if not data:  # If no data is received, it means the client has disconnected
                    break  # Exit the loop

                buffer += data  # Appends the received data to the buffer
                while "\n" in buffer:  # Process the buffer as long as it contains a newline character
                    line, buffer = buffer.split("\n", 1)  # Splits the buffer into the first line and the rest
                    line = line.strip()  # Removes any leading/trailing whitespace and carriage returns
                    if not line:  # If the line is empty after stripping, continue to the next iteration
                        continue

                    if line.upper() == "PING":  # If the command is "PING" (case-insensitive)
                        conn.sendall(b"+PONG\r\n")  # Sends back a "PONG" response
                    else:  # For any other command
                        conn.sendall(b"-ERR Unknown command\r\n")  # Sends an "Unknown command" error
        except Exception as e:  # Catches any exceptions that occur during communication
            print(f"Error with {addr}: {e}", flush=True)  # Prints the error message
        finally:  # This block will always be executed
            conn.close()  # Closes the client connection
            print(f"Disconnected {addr}", flush=True)  # Prints a message that the client has disconnected

    def run(self):  # Method to start the server and accept connections
        try:
            while True:  # Infinite loop to keep the server running
                conn, addr = self.server_socket.accept()  # Accepts a new client connection
                thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)  # Creates a new thread to handle the client
                thread.start()  # Starts the new thread
        except KeyboardInterrupt:  # Catches a Ctrl+C keyboard interrupt
            print("\nShutting down server...", flush=True)  # Prints a shutdown message
        finally:  # This block will always be executed on exit
            self.server_socket.close()  # Closes the main server socket

if __name__ == "__main__":  # If this script is executed directly
    server = TCPServer()  # Creates an instance of the TCPServer
    server.run()  # Runs the server