# File Processing Service


## Description  
  
Simple File Processing Service which takes CSV file as input through RESTAPI - process and store in Database. Authentication and List APIs are created for the user registration, authentication, check progress and list movies with pagination. Python's Flask Framework is used and for database - MongoDB is used.
 

## How to use  

#### Python - 3.10.x version is used
  
1) Clone the repository.

2) Install Python 3.10.x version in local setup 

3) Setup venv - virtual environment

4) Activate the venv (check for the folder where the venv was created)
    ```bash
    source .venv/bin/activate
    ```
   
5) Install project dependencies
    ```bash
    pip install -r requirements.txt
    ```
    This will install all dependent libraries to run the server.

## Usage
  
Start/Run the server

   ```bash
    python3 run /file_upload_imdb_service/bin/imdb_app 
   ```