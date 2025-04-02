from Services.DatabaseConnection import DatabaseConnection

class TransferRecordRepository:
    def create(self, reason_id, user_id, amount: int, note: str = None):
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            """
                INSERT INTO transfer_records 
                    (reason_id, user_id, amount, note, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, 
            (reason_id, user_id, amount, note, currentTimestamp, currentTimestamp)
        )
        connection.commit()
        return cursor.lastrowid
