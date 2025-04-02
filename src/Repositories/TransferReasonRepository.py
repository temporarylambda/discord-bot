from Services.DatabaseConnection import DatabaseConnection
from Enums.TransferRecordType import TransferRecordType

class TransferReasonRepository:
    # 建立轉帳原因並回傳 ID
    def create(self, type: TransferRecordType, reason: str, item_id=None):
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            """
                INSERT INTO transfer_reasons 
                    (type, reason, item_id, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s)
            """, 
            (type.value, reason, item_id, currentTimestamp, currentTimestamp)
        )
        connection.commit()
        return cursor.lastrowid
    
    def createCheckIn(self, reason: str, item_id):
        return self.create(TransferRecordType.CHECK_IN, reason, item_id)
    
    def createTransfer(self, reason: str, item_id=None):
        return self.create(TransferRecordType.TRANSFER, reason, item_id)
    
    def createGive(self, reason: str, item_id=None):
        return self.create(TransferRecordType.GIVE, reason, item_id)
    
    def createTake(self, reason: str, item_id=None):
        return self.create(TransferRecordType.TAKE, reason, item_id)
    
    def createMerchandise(self, reason: str, item_id):
        return self.create(TransferRecordType.MERCHANDISE, reason, item_id)
