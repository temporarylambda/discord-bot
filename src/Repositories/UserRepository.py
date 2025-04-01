from Services.DatabaseConnection import DatabaseConnection

class UserRepository:
    def find(self, uuid, name=None):
        currentTimestamp = DatabaseConnection.getCurrentTimestamp();
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        if name is not None:
            statement = f"UPDATE users SET name = %s, updated_at = %s WHERE uuid = %s AND name != %s";
            cursor.execute(statement, (name, currentTimestamp, uuid, name));
            connection.commit();
        
        # 查詢使用者資料
        statement = f"SELECT * FROM users WHERE uuid = %s LIMIT 1";
        cursor.execute(statement, (uuid,));
        result = cursor.fetchone();
        return result;

    def create(self, uuid, name, balance=0, consecutive_checkin_days=0):
        currentTimestamp = DatabaseConnection.getCurrentTimestamp();
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        statement = f"INSERT INTO users (uuid, name, balance, consecutive_checkin_days, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)";
        cursor.execute(statement, (uuid, name, balance, consecutive_checkin_days, currentTimestamp, currentTimestamp));
        connection.commit();

        return self.find(uuid);
