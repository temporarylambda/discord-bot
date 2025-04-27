from Services.DatabaseConnection import DatabaseConnection
from Enums.GamblerStatus import GamblerStatus
class GamblerRepository:
    def list(self, gambling_id) -> list:
        """
        取得賭局中的所有使用者資料

        :param gambling_id: 賭局 id
        :return: list
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        cursor.execute("SELECT * FROM gamblers WHERE gambling_id = %s", (gambling_id,))
        return cursor.fetchall()

    def get(self, gambling_id, user_id) -> dict: 
        """
        取得使用者在賭局中的資料

        :param gambling_id: 賭局 id
        :param user_id: 使用者 id
        :return: dict
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        cursor.execute("SELECT * FROM gamblers WHERE gambling_id = %s AND user_id = %s", (gambling_id, user_id))
        return cursor.fetchone()

    def find(self, gambler_id) -> dict:
        """
        取得使用者在賭局中的資料
        
        :param gambler_id: 賭局 id
        :return: dict
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute("SELECT * FROM gamblers WHERE id = %s", (gambler_id, ))
        return cursor.fetchone()

    def join(self, gambling_id, user_id) -> dict:
        """
        參加賭局

        :param gambling_id: 賭局 id
        :param user_id: 使用者 id
        :return: dict
        """
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            """
                INSERT INTO gamblers (gambling_id, user_id, status, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s) 
                ON DUPLICATE KEY UPDATE id = id
            """,
            (
                gambling_id, 
                user_id, 
                GamblerStatus.PENDING.value, 
                currentTimestamp, 
                currentTimestamp,
            )
        )
        connection.commit()
        return self.find(cursor.lastrowid) if cursor.lastrowid is not None else self.get(gambling_id, user_id)

    def raiseBet(self, gambling_id, user_id, bet: int) -> dict:
        """
        提高賭注金額

        :param Gambling: 賭局資料
        :type Gambling: dict
        :param User: 使用者資料
        :type User: dict
        :param bet: 提高的賭注金額
        :type bet: int
        :return: dict
        """

        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute("UPDATE gamblers SET total_bets = total_bets + %s, updated_at = %s WHERE gambling_id = %s AND user_id = %s",
            (
                bet,
                currentTimestamp, 
                gambling_id, 
                user_id,
            )
        )
        connection.commit()
        return self.get(gambling_id, user_id)