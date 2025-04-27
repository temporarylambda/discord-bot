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
                ON DUPLICATE KEY UPDATE id = id, status = %s, total_bets = 0, updated_at = %s
            """,
            (
                gambling_id, 
                user_id, 
                GamblerStatus.PENDING.value, 
                currentTimestamp, 
                currentTimestamp,
                GamblerStatus.PENDING.value,
                currentTimestamp
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
        cursor.execute("UPDATE gamblers SET total_bets = IFNULL(total_bets, 0) + %s, updated_at = %s WHERE gambling_id = %s AND user_id = %s",
            (
                bet,
                currentTimestamp, 
                gambling_id, 
                user_id,
            )
        )
        connection.commit()
        return self.get(gambling_id, user_id)
    
    def cancel(self, gambling_id, user_id) -> dict:
        """
        取消參加賭局

        :param gambling_id: 賭局 id
        :param user_id: 使用者 id
        :return: dict
        """
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute("UPDATE gamblers SET status = %s, updated_at = %s WHERE gambling_id = %s AND user_id = %s",
            (
                GamblerStatus.CANCELED.value,
                currentTimestamp, 
                gambling_id, 
                user_id,
            )
        )
        connection.commit()
        return self.get(gambling_id, user_id)

    def start(self, gambling_id) -> None:
        """
        開始賭局

        :param gambling_id: 賭局 id
        :return: dict
        """
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute("UPDATE gamblers SET status = %s, updated_at = %s WHERE gambling_id = %s AND status = %s",
            (
                GamblerStatus.IN_PROGRESS.value,
                currentTimestamp, 
                gambling_id, 
                GamblerStatus.PENDING.value,
            )
        )
        connection.commit()
        return

    def setWinner(self, gambling_id, user_id) -> dict:
        """
        設定使用者為贏家

        :param gambling_id: 賭局 id
        :param user_id: 使用者 id
        :return: dict
        """
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        # 先將所有非指定贏家的參加者狀態設為輸家, 並把贏家標記成贏家
        cursor.execute(
            "UPDATE gamblers SET status = IF(user_id = %s, %s, %s), updated_at = %s WHERE gambling_id = %s AND status = %s",
            (
                user_id,
                GamblerStatus.WINNER.value,
                GamblerStatus.LOSER.value,
                currentTimestamp, 
                gambling_id, 
                GamblerStatus.IN_PROGRESS.value,
            )
        )
        connection.commit()
        return self.get(gambling_id, user_id)
    
    def getTotalBets(self, gambling_id) -> int:
        """
        取得賭局中所有參加者的總賭注金額

        :param gambling_id: 賭局 id
        :return: int
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            "SELECT SUM(total_bets) as totalBets FROM gamblers WHERE gambling_id = %s AND status NOT IN (%s, %s)", 
            (gambling_id, GamblerStatus.CANCELED.value, GamblerStatus.PENDING.value)
        )
        result = cursor.fetchone()
        return int(result['totalBets']) if result is not None else 0