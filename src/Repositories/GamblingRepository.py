from Services.DatabaseConnection import DatabaseConnection
from Enums.GamblingType import GamblingType
from Enums.GamblingStatus import GamblingStatus
class GamblingRepository:

    def findById(self, id: str|int) -> dict:
        """
        根據ID查詢遊戲資訊

        :param id: 遊戲ID
        :return: 遊戲資訊
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute("SELECT * FROM gambling WHERE id = %s", (id,))
        return cursor.fetchone()

    def create(self, user_id: str|int, type: GamblingType, min_bet: str|int, max_bet: str|int) -> dict:
        """
        建立一場遊戲

        :param user_id: 使用者ID
        :param type: 遊戲類型
        :return: 遊戲資訊
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        cursor.execute(
            "INSERT INTO gambling (user_id, status, type, min_bet, max_bet, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
            (user_id, type.value, GamblingStatus.PENDING.value, min_bet, max_bet, currentTimestamp, currentTimestamp)
        )
        connection.commit()
        insertId = cursor.lastrowid

        cursor.execute("SELECT * FROM gambling WHERE id = %s", (insertId,))
        return cursor.fetchone()

    def finish(self, id: str|int) -> None:
        """
        完成一場遊戲

        :param id: 遊戲ID
        """
        return self.__updateStatus(id, GamblingStatus.FINISHED)

    def cancel(self, id: str|int) -> None:
        """
        結束一場遊戲

        :param id: 遊戲ID
        """
        return self.__updateStatus(id, GamblingStatus.CANCELED)

    def start(self, id: str|int) -> None:
        """
        開始一場遊戲

        :param id: 遊戲ID
        """
        return self.__updateStatus(id, GamblingStatus.GAMBLING)
    
    def __updateStatus(self, id: str | int, type: GamblingStatus):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()

        # 如果 type = GamblingStatus.CANCELED，則更新 canceled_at
        updated     = {"status": type.value, "updated_at": currentTimestamp}
        condition   = {"id": id}
        if type == GamblingStatus.CANCELED:
            updated["canceled_at"] = currentTimestamp
        elif type == GamblingStatus.FINISHED:
            updated["finished_at"] = currentTimestamp

        
        # 更新資料庫
        statement, values = DatabaseConnection.createUpdateStatement(
            table="gambling",
            data=updated,
            condition=condition
        )
        cursor.execute(statement, values)
        connection.commit()
        return