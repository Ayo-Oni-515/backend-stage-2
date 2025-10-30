# stage-2-backend
*HNG 13 backend track stage 2*

A publicly accesible RESTful API service that analyzes Country Currency & Exchange API. Implementation was achieved using python's FastAPI framework


## MySQL Setup (For Linux)

1. Update the package index

        sudo apt update

2. Install MySQL using:

        sudo apt install mysql-server

3. Start MySQL Service

        sudo systemctl start mysql

4. Enable MySQL to start on boot

        sudo systemctl enable mysql

5. Run the security script

        sudo mysql_secure_installation

6. Set the details required from you.

7. Access your MySQL using;

        mysql -u root -p

    then enter your password

8. Create the database using:

        CREATE DATABASE <db-name>

9. Set the following property (this is due to autentication issue with pymysql):

        ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';
        FLUSH PRIVILEGES;

10. Set your DATABASE_URL in the .env.sample file and rename to .env using:

        mv .env.sample .env

    Note: make sure yor URL follows this format:

        mysql+pymysql://root:<your_password>@localhost:3306/<db-name>
        

## Local Setup
1. Clone the repository

        git clone https://github.com/Ayo-Oni-515/backend-stage-2.git

2. Create a virtual environment

        python -m venv <environment-name>

3. Activate the virtual environment

        source <environment-name>/Script/activate (on windows)

        source <environment-name>/bin/activate (on linux and Mac)

4. Install dependencies

    Dependencies are available in requirements.txt

    * fastapi[standard]
    * sqlmodel
    * python-dotenv
    * pymysql
    * requests
    * pillow
    * cryptography

    To install dependencies on local machine

        pip install -r requirements.txt

3. Test locally by using this command then click on the localhst link provided in the terminal.

        fastapi run

## API Documentation
To access online, use endpoint URL:

http://18.153.106.69