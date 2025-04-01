from Services.DatabaseConnection import DatabaseConnection

class TopicRepository:
    # 隨機取得一條題目
    def random(self):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute("SELECT * FROM topics ORDER BY RAND() LIMIT 1")
        row = cursor.fetchone()
        return row

    # 取得所有題目
    def create(self, description, reward=50, note=None):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        cursor.execute(
            "INSERT INTO topics (description, reward, note, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)", 
            (description, reward, note, currentTimestamp, currentTimestamp)
        )
        connection.commit()
        return cursor.lastrowid
