import os
import mysql.connector
from datetime import datetime

class DatabaseConnection:
    def connect():
        return mysql.connector.connect(
            host="mysql-db",
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )

    def getCurrentTimestamp():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')