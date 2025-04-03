from Services.DatabaseConnection import DatabaseConnection
from Enums.TransferRelationType import TransferRelationType
from Enums.TransferReasonType import TransferReasonType

class TransferReasonRepository:
    # 建立轉帳原因並回傳 ID
    def create(self, type: TransferReasonType, reason: str):
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            """
                INSERT INTO transfer_reasons 
                    (type, reason, created_at, updated_at) 
                VALUES (%s, %s, %s, %s)
            """, 
            (type.value, reason, currentTimestamp, currentTimestamp)
        )
        connection.commit()
        return cursor.lastrowid
    
    def createCheckIn(self, reason: str):
        return self.create(TransferReasonType.CHECK_IN, reason)
    
    def createTransfer(self, reason: str):
        return self.create(TransferReasonType.TRANSFER, reason)
    
    def createGive(self, reason: str):
        return self.create(TransferReasonType.GIVE, reason)
    
    def createTake(self, reason: str):
        return self.create(TransferReasonType.TAKE, reason)
    
    def createMerchandise(self, reason: str):
        return self.create(TransferReasonType.MERCHANDISE, reason)

    def createRelation(self, transfer_reason_id, relation_type: TransferRelationType, relation_ids: list = []):
        if len(relation_ids) == 0:
            return None

        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        # 如果 relation_id 有多個值，則使用批次插入
        for relation_id in relation_ids:
            cursor.execute(
                """
                    INSERT INTO transfer_relations 
                        (transfer_reason_id, relation_type, relation_id, created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s)
                """, 
                (transfer_reason_id, relation_type.value, relation_id, currentTimestamp, currentTimestamp)
            )
            connection.commit()
        return cursor.rowcount