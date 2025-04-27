from Services.DatabaseConnection import DatabaseConnection
from datetime import timedelta
from Enums.GamblingType import GamblingType
from Enums.GamblingStatus import GamblingStatus
class GamblingRepository:
    def find(self, id: int) -> dict:
        """
        根據 ID 查詢賭局資料

        :param id: 賭局 ID
        :type id: int
        :return: dict
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(f"SELECT * FROM gambling WHERE id = %s", (id,))
        return cursor.fetchone()

    def create(self, user_id, min_bet: int, max_bet: int, type: GamblingType) -> dict:
        """
        建立一筆賭局

        :param user_id: 舉辦賭局的主辦人 users.id
        :param min_bet: 最小賭注金額
        :type min_bet: int
        :param max_bet: 最大賭注金額
        :type max_bet: int
        :param type: GamblingType
        :type type: GamblingType
        :return: dict
        :rtype: dict
        """

        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        # 查詢使用者資料
        statement, values = DatabaseConnection.createInsertStatement(
            table='gambling',
            data={
                'user_id': user_id,
                'min_bet': min_bet,
                'max_bet': max_bet,
                "status": GamblingStatus.PENDING.value,
                'type': type.value,
                'created_at': currentTimestamp,
                'updated_at': currentTimestamp
            }
        )
        cursor.execute(statement, values)
        connection.commit()

        return self.find(cursor.lastrowid)

    def cancel(self, id: int) -> dict:
        """
        取消賭局

        :param id: 賭局 ID
        :type id: int
        :return: dict
        """
        self.__updateStatus(id, GamblingStatus.CANCELED)
        return self.find(id)
    
    def start(self, id: int) -> dict:
        """
        開始賭局

        :param id: 賭局 ID
        :type id: int
        :return: dict
        """
        self.__updateStatus(id, GamblingStatus.IN_PROGRESS)
        return self.find(id)
    
    def finish(self, id: int) -> dict:
        """
        結束賭局

        :param id: 賭局 ID
        :type id: int
        :return: dict
        """
        self.__updateStatus(id, GamblingStatus.FINISHED)
        return self.find(id)

    def __updateStatus(self, id: int, status: GamblingStatus) -> dict:
        """
        更新賭局狀態

        :param id: 賭局 ID
        :type id: int
        :param status: 賭局狀態
        :type status: GamblingStatus
        :return: dict
        """
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            f"UPDATE gambling SET status = %s, updated_at = %s WHERE id = %s",
            (status.value, currentTimestamp, id)
        )
        connection.commit()
        return self.find(id)