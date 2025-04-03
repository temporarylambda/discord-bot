from Services.DatabaseConnection import DatabaseConnection
from Enums.TransferRelationType import TransferRelationType
from Enums.TransferReasonType import TransferReasonType

class TransferReasonRepository:
    # 建立轉帳原因並回傳 ID
    def create(self, type: TransferReasonType, reason: str, item_id=None):
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
        return self.create(TransferReasonType.CHECK_IN, reason, item_id)
    
    def createTransfer(self, reason: str, item_id=None):
        return self.create(TransferReasonType.TRANSFER, reason, item_id)
    
    def createGive(self, reason: str, item_id=None):
        return self.create(TransferReasonType.GIVE, reason, item_id)
    
    def createTake(self, reason: str, item_id=None):
        return self.create(TransferReasonType.TAKE, reason, item_id)
    
    def createMerchandise(self, reason: str, item_id):
        return self.create(TransferReasonType.MERCHANDISE, reason, item_id)

    def createRelation(self, transfer_record_id, transfer_relation_type: TransferRelationType, transfer_relation_ids: list = []):
        if len(transfer_relation_ids) == 0:
            return None
        
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        # 如果 transfer_relation_ids 有多個值，則使用批次插入
        for transfer_relation_id in transfer_relation_ids:
            cursor.execute(
                """
                    INSERT INTO transfer_relations 
                        (transfer_record_id, transfer_relation_type, transfer_relation_id, created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s)
                """, 
                (transfer_record_id, transfer_relation_type.value, transfer_relation_id, currentTimestamp, currentTimestamp)
            )

        return cursor.lastrowid