from connections import DatabaseConn
from os import getenv
from dotenv import load_dotenv

load_dotenv()

database = DatabaseConn(getenv('ADMIN_NAME'), getenv('ADMIN_PASSWORD'))
database.createEmploye("IPN", "admin", "0000", "1234567", "admin")
