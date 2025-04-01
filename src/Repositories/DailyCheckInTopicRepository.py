from Services.DatabaseConnection import DatabaseConnection
from Enums.DailyCheckInTopicStatus import DailyCheckInTopicStatus

class DailyCheckInTopicRepository:
    # 取得目前尚未結束的簽到題目
    def getCurrentTopics(self, discord_id):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            "SELECT "
            "daily_check_in_topics.id,"
            "daily_check_in_topics.discord_id,"
            "daily_check_in_topics.topic_id,"
            "topics.description,"
            "topics.reward,"
            "topics.note,"
            "daily_check_in_topics.status,"
            "daily_check_in_topics.created_at,"
            "daily_check_in_topics.updated_at "
            "FROM daily_check_in_topics "
            "INNER JOIN topics ON topics.id = daily_check_in_topics.topic_id "
            "WHERE discord_id = %s AND status = %s", 
            (discord_id, DailyCheckInTopicStatus.PENDING.value)
        )
        rows = cursor.fetchall()
        return rows
    
    # 取得今天已經建立出的簽到題目
    def getTodayTakenTopics(self, discord_id):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            "SELECT topic_id FROM daily_check_in_topics WHERE discord_id = %s AND DATE(created_at) = CURRENT_DATE", 
            (discord_id,)
        )
        rows = cursor.fetchall()
        return rows
    
    # 完成簽到題目
    def complete(self, discord_id, topic_id):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        cursor.execute(
            "UPDATE daily_check_in_topics SET status = %s, updated_at = %s WHERE discord_id = %s AND topic_id = %s", 
            (DailyCheckInTopicStatus.COMPLETED.value, currentTimestamp, discord_id, topic_id)
        )
        connection.commit()
        return cursor.rowcount
    
    # 跳過簽到題目
    def skip(self, discord_id, topic_id):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        cursor.execute(
            "UPDATE daily_check_in_topics SET status = %s, updated_at = %s WHERE discord_id = %s AND topic_id = %s", 
            (DailyCheckInTopicStatus.SKIP.value, currentTimestamp, discord_id, topic_id)
        )
        connection.commit()
        return cursor.rowcount
    
    # 註冊簽到題目
    def register(self, discord_id, topic_id):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)

        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        cursor.execute(
            "INSERT INTO daily_check_in_topics (discord_id, topic_id, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)", 
            (discord_id, topic_id, DailyCheckInTopicStatus.PENDING.value, currentTimestamp, currentTimestamp)
        )
        connection.commit()
        return cursor.lastrowid
