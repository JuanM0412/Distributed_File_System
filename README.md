# Distributed File System

## Generate and prepare the source code

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
    **Note:** Replace `venvname` with a more appropriate name, such as `p2p_network`.

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

**Note:** For the correct functioning of the last two instructions, it is recommended to go to the `.env` file and change the port so that there are no duplicates. That is, ensure that a data node and the server do not share the same port, or that two data nodes are not using the same port. This will avoid conflicts.