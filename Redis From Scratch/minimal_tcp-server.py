import socket  # Import the socket module for network communication
import threading  # Import the threading module to handle multiple clients concurrently

class TCPServer:  # Defines the TCP server class
    def __init__(self, host='localhost', port=6379):  # Initialize the server with host and port
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the address
            self.server_socket.bind((host, port))  # Bind the socket to the host and port
            self.server_socket.listen(5)  # Listen for incoming connections, with a backlog of 5
            print(f"Server listening on {host}:{port}")  # Print a message that the server is listening
            self.store = {}  # A dictionary to store key-value data
            self.lock = threading.Lock()  # A lock to ensure thread-safe access to the store
        except OSError as e:  # Handle errors that occur during socket creation
            print(f"Error creating socket: {e}")  # Print the error message
            exit(1)  # Exit the program if the socket cannot be created

    def handle_client(self, conn, addr):  # Method to handle a single client connection
        print(f"Connected by {addr}")  # Print the address of the new client
        buffer = ""  # Initialize an empty buffer for incoming data

        try:
            while True:  # Loop to continuously receive data from the client
                data = conn.recv(1024)  # Receive up to 1024 bytes of data
                if not data:  # If no data is received, the client has disconnected
                    break  # Exit the loop

                # Accumulate partial input
                buffer += data.decode(errors='ignore')  # Decode the data and add it to the buffer, ignoring errors

                # Process only complete lines
                while '\n' in buffer:  # Process as long as there are complete lines (ending with newline)
                    line, buffer = buffer.split('\n', 1)  # Split the buffer into the first line and the rest
                    message = line.strip()  # Remove leading/trailing whitespace

                    if not message:  # If the line is empty, skip it
                        continue

                    print(f"Received from {addr}: {message}")  # Print the received message
                    parts = message.split()  # Split the message into parts
                    command = parts[0].upper()  # The command is the first part, in uppercase

                    if command == "PING":  # If the command is PING
                        conn.sendall(b"+PONG\r\n")  # Respond with PONG

                    elif command == "ECHO":  # If the command is ECHO
                        response = " ".join(parts[1:]) if len(parts) > 1 else ""  # Get the string to echo
                        conn.sendall(b"+" + response.encode() + b"\r\n")  # Send the echoed string back

                    elif command == "SET":  # If the command is SET
                        if len(parts) >= 3:  # SET requires a key and a value
                            key = parts[1]  # The key is the second part
                            value = " ".join(parts[2:])  # The value is the rest of the parts
                            with self.lock:  # Acquire the lock for thread-safe writing
                                self.store[key] = value  # Set the key-value pair in the store
                            conn.sendall(b"+OK\r\n")  # Respond with OK
                        else:
                            conn.sendall(b"-ERR SET requires key and value\r\n")  # Error if not enough arguments

                    elif command == "GET":  # If the command is GET
                        if len(parts) >= 2:  # GET requires a key
                            key = parts[1]  # The key is the second part
                            with self.lock:  # Acquire the lock for thread-safe reading
                                value = self.store.get(key)  # Get the value from the store
                            if value is not None:  # If the key exists
                                conn.sendall(b"+" + value.encode() + b"\r\n")  # Send the value back
                            else:
                                conn.sendall(b"$-1\r\n")  # Send null if the key doesn't exist
                        else:
                            conn.sendall(b"-ERR GET requires key\r\n")  # Error if not enough arguments

                    elif command == "DEL":  # If the command is DEL
                        if len(parts) >= 2:  # DEL requires a key
                            key = parts[1]  # The key is the second part
                            with self.lock:  # Acquire the lock for thread-safe modification
                                if key in self.store:  # If the key exists
                                    del self.store[key]  # Delete the key
                                    conn.sendall(b"+OK\r\n")  # Respond with OK
                                else:
                                    conn.sendall(b"$-1\r\n")  # Respond with -1 if key not found
                        else:
                            conn.sendall(b"-ERR DEL requires key\r\n")  # Error if not enough arguments

                    elif command == "QUIT":  # If the command is QUIT
                        conn.sendall(b"+OK Goodbye\r\n")  # Respond with a goodbye message
                        return  # Exit the client handling loop

                    else:  # For any other command
                        conn.sendall(b"-ERR unknown command\r\n")  # Respond with an unknown command error

        except (ConnectionResetError, BrokenPipeError):  # Handle cases where the client disconnects unexpectedly
            pass  # Do nothing, just let the connection close
        except Exception as e:  # Handle other potential exceptions
            print(f"Error with {addr}: {e}")  # Print the error
        finally:
            conn.close()  # Ensure the connection is closed
            print(f"Disconnected {addr}")  # Print a message that the client has disconnected

    def run(self):  # Method to run the server and accept connections
        try:
            while True:  # Loop indefinitely to accept new connections
                conn, addr = self.server_socket.accept()  # Accept a new connection
                thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)  # Create a new thread for the client
                thread.start()  # Start the client thread
        except KeyboardInterrupt:  # Handle Ctrl+C to shut down the server
            print("\nShutting down server...")
        finally:
            self.server_socket.close()  # Close the server socket
            print("Server closed.")


if __name__ == "__main__":  # If the script is run directly
    server = TCPServer()  # Create an instance of the TCPServer
    server.run()  # Run the server