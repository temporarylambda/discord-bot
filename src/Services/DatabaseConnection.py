import os
import mysql.connector
from datetime import datetime
from zoneinfo import ZoneInfo

class DatabaseConnection:
    def connect():
        return mysql.connector.connect(
            host="mysql-db",
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )

    def cursor(connection):
        return connection.cursor(dictionary=True)

    def getCurrentTimestamp():
        return datetime.now(ZoneInfo("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')