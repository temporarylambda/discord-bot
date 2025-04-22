from Services.DatabaseConnection import DatabaseConnection
from Repositories.UserRepository import UserRepository

class TransferRecordRepository:
    def create(self, transfer_reason_id, user_id, amount: int, note: str = None):
        """
        建立轉帳紀錄

        :param transfer_reason_id: 轉帳原因ID
        :param user_id: 使用者ID
        :param amount: 金額
        :type amount: int
        :param note: 備註
        :type note: str
        :return: None
        """

        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        statement, values = DatabaseConnection.createInsertStatement('transfer_records', {
            'transfer_reason_id': transfer_reason_id,
            'user_id': user_id,
            'amount': amount,
            'note': note,
            'created_at': currentTimestamp,
            'updated_at': currentTimestamp
        })
        cursor.execute(statement, values)
        connection.commit()
        return cursor.lastrowid

    def transfer(self, transfer_reason_id, user_id, amount: int, fee: int =0, note=None):
        """
        轉帳紀錄

        :param transfer_reason_id: 轉帳原因ID
        :param user_id: 使用者ID
        :param amount: 金額
        :param fee: 手續費
        :param note: 備註
        :return: None
        """

        # 轉帳紀錄
        self.create(transfer_reason_id, user_id if user_id is not None else None, amount, note)
        
        # 異動扣款對象餘額 - 如果 user_id 為 None，則代表是對系統方的計算，這情況下不需異動 users 餘額，因為沒有對應的 record
        if user_id is not None:
            UserRepositoryObject = UserRepository()
            UserRepositoryObject.increaseBalance(user_id, amount)

        # 手續費 - 若有手續費，則認定由系統收走
        if (fee and int(fee) > 0): 
            self.create(transfer_reason_id, None, fee, note)

        return;