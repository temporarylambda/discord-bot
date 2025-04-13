from Services.DatabaseConnection import DatabaseConnection
from Enums.GamblerStatus import GamblerStatus

class GamblerRepository:
    def join(self, user_id: str | int, gambling_id: str | int, total_bets: int) -> dict:
        """
        加入遊戲

        :param user_id: 使用者ID
        :param gambling_id: 遊戲ID
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()

        statement, values = DatabaseConnection.createInsertStatement(
            "gamblers",
            {
                "gambling_id": gambling_id,
                "user_id": user_id,
                "total_bets": total_bets,
                "status": GamblerStatus.PENDING.value,
                "created_at": currentTimestamp,
                "updated_at": currentTimestamp
            }
        )
        cursor.execute(statement, values)
        connection.commit()
        return cursor.lastrowid

    def get(self, user_id: str | int, gambling_id: str | int) -> dict:
        """
        取得使用者的賭客資料

        :param user_id: 使用者ID
        :param gambling_id: 遊戲ID
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            "SELECT * FROM gamblers WHERE gambling_id = %s AND user_id = %s", 
            (gambling_id, user_id)
        )
        return cursor.fetchone()

    def raiseBet(self, user_id: str | int, gambling_id: str | int, amount: int) -> dict:
        """
        提高賭注

        :param user_id: 使用者ID
        :param gambling_id: 遊戲ID
        :param amount: 提高的金額
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()

        statement, values = DatabaseConnection.createUpdateStatement(
            'gamblers',
            {
                "total_bets": amount,
                "updated_at": currentTimestamp
            },
            {
                "gambling_id": gambling_id,
                "user_id": user_id
            }
        )
        cursor.execute(statement, values)
        connection.commit()
        return

    def startGame(self, gambling_id: str | int) -> dict:
        """
        開始遊戲

        :param gambling_id: 遊戲ID
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        statement, values = DatabaseConnection.createUpdateStatement(
            'gamblers', 
            {'status': GamblerStatus.GAMBLING.value, 'updated_at': DatabaseConnection.getCurrentTimestamp()}, 
            {'gambling_id': gambling_id}
        )
        cursor.execute(statement, values)
        connection.commit()
        return