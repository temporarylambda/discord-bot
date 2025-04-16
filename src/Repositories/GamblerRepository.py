from typing import Union, List
from Services.DatabaseConnection import DatabaseConnection
from Enums.GamblerStatus import GamblerStatus

class GamblerRepository:
    def join(self, user_id: str | int, gambling_id: str | int, total_bets: int):
        """
        加入遊戲

        :param user_id: 使用者ID
        :param gambling_id: 遊戲ID
        :param total_bets: 賭金
        :return: gambler.id
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

    def get(self, gambling_id: Union[str, int], user_ids: List[Union[str, int]] = []) -> list:
        """
        取得使用者的賭客資料

        :param gambling_id: 遊戲ID
        :param user_ids: 使用者ID 清單（可選）
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        # 基本查詢條件與參數
        sql = """
            SELECT gamblers.*, users.name, users.uuid
            FROM gamblers 
            INNER JOIN users ON gamblers.user_id = users.id
            WHERE gambling_id = %s
        """
        params = [gambling_id]

        # 若有傳入 user_ids，就加上 user_id IN (...)
        if user_ids:
            placeholders = ', '.join(['%s'] * len(user_ids))  # e.g. %s, %s, %s
            sql += f" AND user_id IN ({placeholders})"
            params.extend(user_ids)

        cursor.execute(sql, params)
        results = cursor.fetchall()
        return results

    def raiseBet(self, user_id: str | int, gambling_id: str | int, amount: int) -> None:
        """
        提高賭注

        :param user_id: 使用者ID
        :param gambling_id: 遊戲ID
        :param amount: 提高的金額
        :return: None
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

    def exit(self, user_id: str | int, gambling_id: str | int, is_refund: bool = False) -> None:
        """
        退出遊戲

        :param user_id: 使用者ID
        :param gambling_id: 遊戲ID
        :param is_refund: 是否退款
        :return: None
        """
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()

        condition       = {"gambling_id": gambling_id, "user_id": user_id}
        updatedValue    = {"status": GamblerStatus.ABSTAIN.value, "updated_at": currentTimestamp}
        if (is_refund):
            updatedValue['total_bets'] = 0
        statement, values = DatabaseConnection.createUpdateStatement(
            'gamblers',
            updatedValue,
            condition
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