import os
import mysql.connector
from datetime import datetime
from zoneinfo import ZoneInfo

class DatabaseConnection:
    @staticmethod
    def connect():
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            port=os.getenv("MYSQL_PORT")
        )

    @staticmethod
    def cursor(connection):
        return connection.cursor(dictionary=True)

    @staticmethod
    def getCurrentDateTimeObject():
        return datetime.now(ZoneInfo("Asia/Taipei"))

    @staticmethod
    def getCurrentTimestamp():
        return DatabaseConnection.getCurrentDateTimeObject().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def createUpdateStatement(
        table: str,
        data: dict,
        condition: dict,
        is_allow_full_table_update: bool = False
    ) -> tuple[str, list]:
        """
        給與定義的資料表、更新的資料、條件，產生 SQL 更新語句

        :param table: 資料表名稱
        :param data: 更新的資料，key 為欄位名稱，value 為欄位值
        :param condition: 條件，key 為欄位名稱，value 為欄位值
        :param is_allow_full_table_update: 是否允許全表更新
        :return: SQL 語句和參數列表
        """
        if not table:
            raise ValueError("table must not be empty")
        elif not data:
            raise ValueError("data must not be empty")
        elif not condition and not is_allow_full_table_update:
            raise ValueError("condition must not be empty (unless full-table updates are explicitly allowed)")

        set_clause = ', '.join(f"{key} = %s" for key in data)
        where_clause = "1 = 1" if not condition else " AND ".join(f"{key} = %s" for key in condition)
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        values = list(data.values()) + list(condition.values())
        return sql, values
    
    @staticmethod
    def createInsertStatement(
        table: str,
        data: dict
    ) -> tuple[str, list]:
        """
        給與定義的資料表、插入的資料，產生 SQL 插入語句

        :param table: 資料表名稱
        :param data: 插入的資料，key 為欄位名稱，value 為欄位值
        :return: SQL 語句和參數列表
        """
        if not table:
            raise ValueError("table must not be empty")
        elif not data:
            raise ValueError("data must not be empty")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = list(data.values())
        return sql, values
