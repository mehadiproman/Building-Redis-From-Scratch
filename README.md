
````markdown
# Redis-Like Server in Python

A Redis-like server built from scratch using Python.  
This project explores the internals of Redis, including TCP networking, in-memory data structures, event loops, and persistence mechanisms. It serves as a learning resource for backend developers, DevOps engineers, and system designers interested in understanding high-performance in-memory databases.

---

## Features

- Building a Minimal TCP Server in Python  
- Single-Threaded TCP Server with Event Loop  
- In-Memory Storage with TTL and Background Key Expiration  
- Redis AOF (Append Only File) Persistence  
- Redis RDB (Snapshot) Persistence  
- Implementation of Redis Native Data Structures  
- Publish/Subscribe Messaging System  

---

## Learning Objectives

- Understand how Redis manages data in memory and handles persistence  
- Learn to design and implement a TCP server with an event loop  
- Explore caching techniques and TTL-based key expiration  
- Gain hands-on experience with AOF and RDB persistence models  
- Study the core principles of event-driven architecture  

---

## Tech Stack

- Language: Python 3  
- Core Modules: `socket`, `select`, `threading`, `json`, `time`, `os`  
- Testing Framework: `pytest`  
- Persistence: Custom AOF and RDB logic  

---

## Project Structure

    redis-python-clone/
        ├── src/
        │   ├── server.py            # TCP server and event loop
        │   ├── storage.py           # In-memory data store with TTL
        │   ├── commands.py          # Redis command implementations
        │   ├── persistence/
        │   │   ├── aof.py           # Append-only file persistence
        │   │   └── rdb.py           # RDB snapshot persistence
        │   └── pubsub.py            # Publish/Subscribe logic
        ├── tests/
        │   └── test_commands.py     # Unit tests
        ├── README.md
        └── requirements.txt

---

## Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/redis-python-clone.git

# Navigate into the project directory
cd redis-python-clone

# (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
````

---

## Usage

Start the server:

```bash
python src/server.py
```

Connect to it using a client (for example, `telnet` or `redis-cli`):

```bash
telnet localhost 6379
```

Example commands:

```
SET name "Mehedi"
GET name
EXPIRE name 10
PUBLISH channel1 "Hello World"
```

---

## Future Enhancements

* Additional Redis data structures (e.g., Sorted Sets, Streams)
* Cluster and replication support
* Command pipelining
* Authentication and access control

---

## Author

**Mehedi Hasan Proman**
Aspiring Back-end & Cloud Engineer
Focused on system design, distributed systems, and cloud infrastructure & automation.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

