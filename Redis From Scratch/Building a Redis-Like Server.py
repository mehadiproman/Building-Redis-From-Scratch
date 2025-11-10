import socket  # Import the socket module for network connections
import select  # Import the select module for I/O multiplexing
import errno  # Import the errno module for error codes

class RedisLikeServer:  # Defines the main class for our Redis-like server
    def __init__(self, host='localhost', port=6379):  # Initializes the server with a host and port
        # Basic server configuration
        self.host = host  # The hostname or IP address to bind to (default: localhost)
        self.port = port  # The port number to listen on (default: 6379, the standard Redis port)
        self.running = True  # A flag to control the main server loop

        # Data structures for managing clients and storage
        self.client_sockets = set()  # A set to store all connected client sockets
        self.client_buffers = {}  # A dictionary to buffer incoming data from clients
        self.client_addresses = {}  # A dictionary to map client sockets to their addresses
        self.store = {}  # A dictionary to store key-value data, acting as the Redis-like database

    def start(self):  # Method to initialize and start the server
        """Initialize and start the server."""
        # Create a TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a new TCP/IP socket
        # Allow reuse of the same address after restart
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allows the socket to be reused immediately after it's closed - Server বন্ধ → আবার চালালে port reuse করা যাবে
        # Set non-blocking mode
        self.server_socket.setblocking(False)  # Set the socket to non-blocking mode to handle multiple clients - Socket non-blocking → একাধিক client handle সম্ভব
        # Bind to the specified host and port
        self.server_socket.bind((self.host, self.port))  # Bind the socket to the configured host and port
        # Start listening for incoming connections
        self.server_socket.listen(128)  # Listen for incoming connections, with a backlog of 128 - Client accept করার জন্য queue তৈরি (max 128 waiting client)

        print(f"Single-threaded Redis-like server listening on {self.host}:{self.port}")  # Print a message indicating the server is running
        self._event_loop()  # Start the main event loop

    def _event_loop(self):  # The main event loop for handling I/O
        """Main event loop using select() for I/O multiplexing."""
        while self.running:  # Loop as long as the server is running
            # Monitor readable sockets (server + all clients)
            readable = [self.server_socket] + list(self.client_sockets)  # Sockets to check for readability (new connections or incoming data)
            writable = []  # Sockets to check for writability (we are not using this here)
            errors = list(self.client_sockets)  # Sockets to check for errors

            # Wait for socket events (1-second timeout)
            ready_read, ready_write, error_sockets = select.select(readable, writable, errors, 1.0)  # Use select to wait for I/O events

            # Handle new client connections
            if self.server_socket in ready_read:  # If the server socket is readable, it means there's a new connection
                self._accept_new_connection()  # Accept the new connection

            # Handle data from connected clients
            for client_socket in ready_read:  # Iterate over sockets with incoming data
                if client_socket != self.server_socket:  # If it's a client socket
                    self._handle_client_data(client_socket)  # Handle the data from that client

            # Handle socket errors
            for sock in error_sockets:  # Iterate over sockets with errors
                self._disconnect_client(sock)  # Disconnect the client

    def _accept_new_connection(self):  # Method to accept a new client connection
        """Accept new incoming client connections."""
        try:
            client_socket, address = self.server_socket.accept()  # Accept the connection
            client_socket.setblocking(False)  # Set the new client socket to non-blocking mode

            # Track the new client
            self.client_sockets.add(client_socket)  # Add the new client socket to our set of clients
            self.client_buffers[client_socket] = ""  # Initialize an empty buffer for the client
            self.client_addresses[client_socket] = address  # Store the client's address

            print(f"New connection from {address}")  # Print a message about the new connection
            self._send_to_client(client_socket, "+OK Redis-like server ready\r\n")  # Send a welcome message to the client

        except socket.error:  # Handle potential errors during accept
            pass  # Ignore errors for now

    def _handle_client_data(self, client_socket):  # Method to handle data received from a client
        """Read and process data from a client."""
        try:
            data = client_socket.recv(4096).decode('utf-8')  # Receive up to 4096 bytes of data and decode it
            if not data:  # If no data is received, the client has disconnected
                self._disconnect_client(client_socket)  # Disconnect the client
                return  # Stop processing for this client

            # Accumulate partial data in buffer
            self.client_buffers[client_socket] += data  # Add the received data to the client's buffer
            # Process complete commands
            self._process_client_buffer(client_socket)  # Process the buffer for complete commands

        except socket.error as e:  # Handle socket errors
            if e.errno != errno.EWOULDBLOCK:  # If the error is not a "would block" error (meaning no data to read)
                self._disconnect_client(client_socket)  # Disconnect the client

    def _process_client_buffer(self, client_socket):  # Method to process the command buffer for a client
        """Process commands from the client's buffer."""
        buffer = self.client_buffers[client_socket].replace('\r\n', '\n')  # Normalize line endings

        while '\n' in buffer:  # Process as long as there are complete lines in the buffer
            line, buffer = buffer.split('\n', 1)  # Split the buffer into the first line and the rest
            message = line.strip()  # Remove leading/trailing whitespace from the command

            if not message:  # If the message is empty, continue to the next line
                continue

            self._execute_command(client_socket, message)  # Execute the command

        # Update remaining partial buffer
        self.client_buffers[client_socket] = buffer  # Store any remaining partial command back in the buffer

    def _execute_command(self, client_socket, message):  # Method to execute a single command
        """Parse and execute a single command."""
        parts = message.split()  # Split the command into parts
        command = parts[0].upper()  # The command is the first part, converted to uppercase

        if command == "PING":  # Handle the PING command
            self._send_to_client(client_socket, "+PONG\r\n")  # Respond with PONG

        elif command == "ECHO":  # Handle the ECHO command
            response = " ".join(parts[1:]) if len(parts) > 1 else ""  # Get the message to echo
            self._send_to_client(client_socket, f"+{response}\r\n")  # Send the echoed message back

        elif command == "SET":  # Handle the SET command
            if len(parts) >= 3:  # SET requires a key and a value
                key = parts[1]  # The key is the second part
                value = " ".join(parts[2:])  # The value is the rest of the command
                self.store[key] = value  # Store the key-value pair
                self._send_to_client(client_socket, "+OK\r\n")  # Respond with OK
            else:
                self._send_to_client(client_socket, "-ERR SET requires key and value\r\n")  # Send an error if syntax is wrong

        elif command == "GET":  # Handle the GET command
            if len(parts) >= 2:  # GET requires a key
                key = parts[1]  # The key is the second part
                value = self.store.get(key)  # Get the value from the store
                if value is not None:  # If the key exists
                    self._send_to_client(client_socket, f"+{value}\r\n")  # Send the value
                else:
                    self._send_to_client(client_socket, "$-1\r\n")  # Send a null bulk string if the key doesn't exist
            else:
                self._send_to_client(client_socket, "-ERR GET requires key\r\n")  # Send an error if syntax is wrong

        elif command == "DEL":  # Handle the DEL command
            if len(parts) >= 2:  # DEL requires a key
                key = parts[1]  # The key is the second part
                if key in self.store:  # If the key exists in the store
                    del self.store[key]  # Delete the key
                    self._send_to_client(client_socket, "+OK\r\n")  # Respond with OK
                else:
                    self._send_to_client(client_socket, "$-1\r\n")  # Respond with -1 if key not found
            else:
                self._send_to_client(client_socket, "-ERR DEL requires key\r\n")  # Send an error if syntax is wrong

        elif command == "QUIT":  # Handle the QUIT command
            self._send_to_client(client_socket, "+OK Goodbye\r\n")  # Respond with a goodbye message
            self._disconnect_client(client_socket)  # Disconnect the client

        else:  # Handle unknown commands
            self._send_to_client(client_socket, "-ERR unknown command\r\n")  # Send an error for any other command

    def _send_to_client(self, client_socket, message):  # Method to send a message to a client
        """Send a response to a client."""
        try:
            client_socket.sendall(message.encode())  # Encode the message to bytes and send it
        except socket.error:  # Handle errors during sending
            self._disconnect_client(client_socket)  # Disconnect the client if sending fails

    def _disconnect_client(self, client_socket):  # Method to disconnect a client
        """Remove a disconnected client from all records."""
        address = self.client_addresses.get(client_socket, "Unknown")  # Get the client's address for logging
        print(f"Disconnected {address}")  # Print a message about the disconnection

        if client_socket in self.client_sockets:  # If the client is in our set of sockets
            self.client_sockets.remove(client_socket)  # Remove it
        self.client_buffers.pop(client_socket, None)  # Remove the client's buffer
        self.client_addresses.pop(client_socket, None)  # Remove the client's address mapping

        try:
            client_socket.close()  # Close the socket connection
        except socket.error:  # Handle potential errors during close
            pass  # Ignore errors


if __name__ == "__main__":  # If this script is executed directly
    server = RedisLikeServer()  # Create an instance of the server
    server.start()  # Start the server
