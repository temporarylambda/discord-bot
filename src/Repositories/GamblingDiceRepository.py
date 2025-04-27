from Services.DatabaseConnection import DatabaseConnection
from datetime import timedelta
from Enums.GamblingType import GamblingType
from Enums.GamblingStatus import GamblingStatus
class GamblingDiceRepository:
    def remove(self, gambling_id: int, user_id: int) -> None:
        """
        刪除擲骰資料

        :param gambling_id: 賭局 ID
        :type gambling_id: int
        :param user_id: 使用者 ID
        :type user_id: int
        :return: None
        :rtype: None
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute("DELETE FROM gambling_dices WHERE id = %s AND user_id = %s", (gambling_id, user_id))
        connection.commit()
        return

    def upsert(self, gambling_id: int, user_id: int, dices: list = []) -> None:
        """
        改寫擲骰紀錄

        - 會先移除所有該使用者在該賭局的擲骰紀錄
        - 再新增該使用者在該賭局的擲骰紀錄

        :param gambling_id: 賭局 ID
        :type gambling_id: int
        :param user_id: 使用者 ID
        :type user_id: int
        :param dices: 骰子列表
        :type dices: list
        :return: None
        :rtype: None
        """
        if not dices:
            raise ValueError("Dices cannot be empty")
        
        self.remove(gambling_id, user_id)
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        for dice in dices:
            cursor.execute(
                "INSERT INTO gambling_dices (gambling_id, user_id, dice, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                (
                    gambling_id,
                    user_id,
                    dice,
                    currentTimestamp,
                    currentTimestamp,
                )
            )
            connection.commit()
        
        return
    
    def ranking(self, gambling_id: int, limit: int = 1, sort_order: str = "DESC") -> list:
        """
        取得該賭局的最大擲骰紀錄

        :param gambling_id: 賭局 ID
        :type gambling_id: int
        :param limit: 取出排名前幾名
        :type limit: int
        :return: 擲骰紀錄列表
        :rtype: list
        """
        sort_order = "ASC" if sort_order == "ASC" else "DESC"

        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            f"""
                SELECT gambling_id, user_id, SUM(dice) as sum_dices 
                FROM gambling_dices 
                WHERE gambling_id = %s 
                GROUP BY gambling_id, user_id 
                ORDER BY sum_dices {sort_order} 
                LIMIT %s
            """,
            (gambling_id, limit)
        )
        return cursor.fetchall()