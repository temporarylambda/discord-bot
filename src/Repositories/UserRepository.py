from Services.DatabaseConnection import DatabaseConnection
from datetime import timedelta
class UserRepository:
    # 以 discord uuid 進行查詢, 如果沒有資料則建立一筆新的資料
    def findByUUID(self, uuid, name=None):
        currentTimestamp = DatabaseConnection.getCurrentTimestamp();
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        # 查詢使用者資料
        statement = f"SELECT * FROM users WHERE uuid = %s LIMIT 1";
        cursor.execute(statement, (uuid,));
        result = cursor.fetchone();

        # 如果有使用者資料，且名稱不為空，而且資料庫中的名稱與傳入的名稱不相同，則更新名稱
        if result is not None and name is not None and result['name'] != name:
            statement = f"UPDATE users SET name = %s, updated_at = %s WHERE uuid = %s AND name != %s";
            cursor.execute(statement, (name, currentTimestamp, uuid, name));
            connection.commit();
        
        return result;

    # 以 id 進行查詢
    def findById(self, id):
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        statement = f"SELECT * FROM users WHERE id = %s LIMIT 1";
        cursor.execute(statement, (id,));
        result = cursor.fetchone();
        return result;

    # 建立資料
    def create(self, uuid, name, balance=0, consecutive_checkin_days=0):
        currentTimestamp = DatabaseConnection.getCurrentTimestamp();
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        statement = f"INSERT INTO users (uuid, name, balance, consecutive_checkin_days, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)";
        cursor.execute(statement, (uuid, name, balance, consecutive_checkin_days, currentTimestamp, currentTimestamp));
        connection.commit();

        return self.findByUUID(uuid);

    # 簽到用，更新資料
    def checkIn(self, user_id):
        currentDatetimeObject = DatabaseConnection.getCurrentDateTimeObject();
        currentDate = currentDatetimeObject.strftime('%Y-%m-%d');
        currentTimestamp = currentDatetimeObject.strftime('%Y-%m-%d %H:%M:%S');
        yesterday = (currentDatetimeObject - timedelta(days=1)).strftime('%Y-%m-%d');

        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        # 如果 DATE(lastest_checkin_at) 等於昨天，則連續簽到天數加 1，否則重置為 1
        cursor.execute(
            f"""
                UPDATE users 
                SET consecutive_checkin_days = IF(DATE(latest_checkin_at) = %s, consecutive_checkin_days + 1, 1), 
                    latest_checkin_at = %s, updated_at = %s 
                WHERE id = %s AND (DATE(latest_checkin_at) != %s OR latest_checkin_at IS NULL)
            """, 
            (yesterday, currentTimestamp, currentTimestamp, user_id, currentDate)
        );
        connection.commit();

    # 異動金額用
    def increaseBalance(self, user_id, amount):
        currentTimestamp = DatabaseConnection.getCurrentTimestamp();
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        statement = f"UPDATE users SET balance = balance + %s, updated_at = %s WHERE id = %s";
        cursor.execute(statement, (amount, currentTimestamp, user_id));
        connection.commit();

    # 取得伺服器中最有錢的使用者
    def getRichestUsers(self, limit: int = 1):
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        cursor.execute("SELECT * FROM users WHERE balance > 0 ORDER BY balance DESC LIMIT %s", (limit,));
        result = cursor.fetchall();
        return result;

    # 取得伺服器中連續簽到天數最多的使用者
    def getCheckInChampions(self, limit: int = 1):
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        cursor.execute("SELECT * FROM users WHERE consecutive_checkin_days > 0 ORDER BY consecutive_checkin_days DESC LIMIT %s", (limit,));
        result = cursor.fetchall();
        return result;

    @staticmethod
    def resetDailyCheckIn():
        currentDatetimeObject = DatabaseConnection.getCurrentDateTimeObject();
        currentTimestamp = currentDatetimeObject.strftime('%Y-%m-%d %H:%M:%S');
        yesterday = (currentDatetimeObject - timedelta(days=1)).strftime('%Y-%m-%d');

        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        # 撈取所有簽到日期不是昨天的使用者，把連續簽到天數重置為 0
        cursor.execute(
            "UPDATE users SET consecutive_checkin_days = 0, updated_at = %s WHERE (DATE(latest_checkin_at) != %s AND DATE(latest_checkin_at) != %s) AND consecutive_checkin_days > 0",
            (currentTimestamp, yesterday, currentTimestamp)
        );
        connection.commit();