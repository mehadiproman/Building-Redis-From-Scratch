````markdown
# Redis-Like Server in Python

A Redis-like server built from scratch using Python.

This project explores the internals of Redis, including TCP networking, in-memory data structures, event loops, and persistence mechanisms. It serves as a learning resource for backend developers, DevOps engineers, and system designers interested in understanding high-performance in-memory databases.

---

## Features

-   **Minimal TCP Server**: Built from the ground up using Python's native `socket` module.
-   **Event Loop**: A single-threaded, non-blocking event loop to handle multiple client connections concurrently.
-   **In-Memory Storage**: A dictionary-based data store with support for Time-To-Live (TTL) and background key expiration.
-   **AOF Persistence**: Append-Only File (AOF) persistence to log every write operation.
-   **RDB Persistence**: RDB-style snapshotting for point-in-time backups.
-   **Native Data Structures**: Implementation of core Redis data types (e.g., Strings, Lists).
-   **Publish/Subscribe**: A messaging system allowing clients to subscribe to channels and receive messages.

---

## Learning Objectives

-   Understand how Redis manages data in memory and handles persistence.
-   Learn to design and implement a TCP server with an event loop.
-   Explore caching techniques and TTL-based key expiration.
-   Gain hands-on experience with AOF and RDB persistence models.
-   Study the core principles of event-driven architecture.

---

## Tech Stack

-   **Language**: Python 3
-   **Core Modules**: `socket`, `select`, `threading`, `json`, `time`, `os`
-   **Testing Framework**: `pytest`
-   **Persistence**: Custom AOF and RDB logic

---

## Project Structure

redis-python-clone/
├── src/
│   ├── server.py           # TCP server and event loop
│   ├── storage.py          # In-memory data store with TTL
│   ├── commands.py         # Redis command implementations
│   ├── pubsub.py           # Publish/Subscribe logic
│   └── persistence/
│       ├── aof.py          # Append-only file persistence
│       └── rdb.py          # RDB snapshot persistence
├── tests/
│   └── test_commands.py    # Unit tests
├── README.md
└── requirements.txt
````

-----

## Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/](https://github.com/)<your-username>/redis-python-clone.git
    ```

2.  **Navigate into the project directory:**

    ```bash
    cd redis-python-clone
    ```

3.  **(Optional) Create and activate a virtual environment:**

    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate
    ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

-----

## Usage

1.  **Start the server:**

    ```bash
    python src/server.py
    ```

    By default, the server will start on `127.0.0.1:6379`.

2.  **Connect with a Redis client:**
    You can use `redis-cli` or any other Redis client to connect to the server.

    ```bash
    redis-cli
    ```

3.  **Interact with the server:**
    Once connected, you can run supported Redis commands.

    ```
    127.0.0.1:6379> SET mykey "Hello, World!"
    OK
    127.0.0.1:6379> GET mykey
    "Hello, World!"
    127.0.0.1:6379> SETEX mykey 10 "Expiring Value"
    OK
    ```

-----

## Running Tests

To ensure everything is working as expected, run the test suite using `pytest`.

```bash
pytest
```

-----

## Contributing

Contributions are welcome\! If you have suggestions for improvements or find any bugs, please feel free to open an issue or submit a pull request.

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a pull request.

-----

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

```
```
