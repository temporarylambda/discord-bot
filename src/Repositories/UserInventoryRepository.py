from Enums.UserInventoryStatus import UserInventoryStatus
from Services.DatabaseConnection import DatabaseConnection
class UserInventoryRepository:
    def addMerchandise(self, user_id, merchandise):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        currentTimestamp = DatabaseConnection.getCurrentTimestamp()

        cursor.execute(
            """
                INSERT INTO user_inventories (
                    user_id, 
                    merchandise_id, 
                    status, 
                    created_at, 
                    updated_at
                ) 
                VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, merchandise['id'], UserInventoryStatus.PENDING.value, currentTimestamp, currentTimestamp)
        )
        connection.commit()
        return cursor.lastrowid