<div align="center">

# Distributed File System

</div>

### ST0263-242 Tópicos Especiales en Telemática

### Students:
- Juan Manuel Gómez P. (jmgomezp@eafit.edu.co)
- Miguel Ángel Hoyos V. (mahoyosv@eafit.edu.co)
- Santiago Neusa R. (sneusar@eafit.edu.co)
- Sebastian Restrepo O. (srestrep74@eafit.edu.co)
- Luisa Maria Alvarez G. (lmalvarez8@eafit.edu.co)

### Professor:
- Edwin Nelson Montoya M. (emontoya@eafit.edu.co)

## 1. Project Overview
This project aims to design and implement a minimalist block-based distributed file system (DFS). A DFS allows concurrent access and sharing of files stored across multiple nodes. Among the most mature and widely-used DFS implementations are NFS (Network File System), and AFS (Andrew File System). Our DFS project will take inspiration from modern distributed file systems such as GFS (Google File System) and HDFS (Hadoop Distributed File System), focusing on simplicity and minimalism.

This DFS follows a block-based design but incorporates key characteristics from object storage systems, specifically the Write-Once-Read-Many (WORM) model commonly found in services like AWS S3. Files are split into blocks, and those blocks are distributed across different data nodes, with replication to ensure fault tolerance and data redundancy.

### 1.1. Key Features

- **Block-Based Architecture:** Files are partitioned into blocks and distributed across different data nodes, allowing parallel reading and writing operations.
- **Replication for Fault Tolerance:** Each block is replicated across at least two data nodes, ensuring the system can tolerate node failures.
- **WORM (Write-Once-Read-Many):** Similar to object storage systems, files in this DFS are primarily written once and then read multiple times. Partial file updates are not supported.
- **Client-DataNode Communication:** Clients directly interact with DataNodes for file reading and writing operations. The NameNode, which acts as a central manager, provides metadata and the locations of file blocks to the client.
- **Leader-Follower Replication Model:** When a block is written to a DataNode, it becomes the "Leader" of that block, and it replicates the block to a "Follower" DataNode for redundancy.
- **Basic Command-Line Interface (CLI):** A minimalistic CLI is provided for basic file operations, including ls, cd, put, get, mkdir, rmdir, and rm.
- **Basic Authentication:** Simple user authentication (username/password) is implemented to ensure that each user can only view and manipulate their files.

## 2. High-Level Desing (Architecture)
![image](https://github.com/user-attachments/assets/33bac8c1-f909-489c-a61d-44b7ec3c1dce)
![image](https://github.com/user-attachments/assets/c6d76555-f699-48fb-af33-9eee92238b6b)


## 3. Description of the development and technical environment: programming language, libraries, packages, etc.

### 3.1. Generate and prepare the source code

1. Clone the repository:
    ```
    git clone https://github.com/JuanM0412/Distributed_File_System.git
    ```

2. Access the directory created as a result of the previous step:
    ```
    cd Distributed_File_System
    ```

3. Rename the `.env.example` file to `.env`:
    ```
    mv .env.example .env
    ```

4. Modify the `.env` file as needed.

5. Create and activate a virtual environment:
    ```
    python -m venv venvname
    source venvname/bin/activate
    ```
    **Note:** Replace `venvname` with a more appropriate name, such as `file_system`.

6. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```

7. Run the server:
    ```
    python name_node.py
    ```

8. Run a data node:
    ```
    python data_node.py
    ```

9. Run a client:
    ```
    python client.py
    ```

### 3.2. Development and technical details

Python (3.12.x) was used as programming language and gRPC (1.66.0) as RPC middleware. Among the most relevant libraries used were the native Python libraries, such as pydantic (2.9.1), dotenv (1.0.1), pymongo (4.8.0) and tomli (2.0.1), among others necessary for the implementation of certain functionalities (each of these libraries can be found in the `requirements.txt` file). A high coupling in the development was avoided. In addition, for the demonstration the data node, name node, and client were deployed on EC2 (Ubuntu 24.04) AWS instances.

### 3.3. Parameters

As for the program parameters, there is a file called `.env.example` that must be renamed to `.env`. Within this file are the project execution parameters, which include the attributes of the name node, client, and data node, such as the IP address, port, block size, and the directories where the blocks will be stored, among others. In addition, there are also the parameters for the database connection.

## 4. Video support
- https://youtu.be/6sVKTpLxui0
