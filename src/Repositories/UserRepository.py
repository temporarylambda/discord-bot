from Services.DatabaseConnection import DatabaseConnection
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

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
        if result is not None and ((name is not None and result['name'] != name) or result['deleted_at'] is not None):
            updateData = {'deleted_at': None, 'updated_at': currentTimestamp}
            if name is not None and result['name'] != name:
                updateData['name'] = name

            statement, values = DatabaseConnection.createUpdateStatement(table='users', data=updateData, condition={'uuid': uuid},);
            cursor.execute(statement, values);
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

        return self.findByUUID(uuid, name);

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
        if user_id is None:
            return;

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

    def getInactive(self, days=30):
        """
        getInactive 取得不活躍使用者的資料

        :param days: 不活躍的天數，預設為 30 天
        :return: 不活躍使用者的資料列表
        例如：
        [
            {'id': 1, 'name': 'User1', ...},
            {'id': 2, 'name': 'User2', ...},
            ...
        ]
        """
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        # 取得檢查開始日日期
        currentDatetimeObject = DatabaseConnection.getCurrentDateTimeObject()
        startAt   = (currentDatetimeObject - timedelta(days=int(days))).strftime('%Y-%m-%d 00:00:00')
        statement  = """
            SELECT * FROM users 
            WHERE 
                (latest_checkin_at IS NULL OR latest_checkin_at <= %s) AND 
                (latest_message_at IS NULL OR latest_message_at <= %s) AND 
                deleted_at IS NULL
            ORDER BY latest_checkin_at DESC
        """
        parameters = (startAt, startAt)
        
        cursor.execute(statement, parameters);
        result = cursor.fetchall();
        return result

    def getInactivePaginates(self, days=30, page: int = 1, page_size: int = 10):
        """
        getInactivePaginates 取得不活躍使用者的分頁資料

        :param days: 不活躍的天數，預設為 30 天
        :param page: 分頁頁碼，預設為 1
        :param page_size: 每頁顯示的資料數量，預設為 10
        :return: 包含總數量、當前頁碼、每頁大小和結果的字典
        例如：
        {
            'total_count': 100,
            'page': 1,
            'page_size': 10,
            'result': [
                {'id': 1, 'name': 'User1', ...},
                {'id': 2, 'name': 'User2', ...},
                ...
            ]
        }
        """
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        # 取得檢查開始日日期
        currentDatetimeObject = DatabaseConnection.getCurrentDateTimeObject()
        startAt   = (currentDatetimeObject - timedelta(days=int(days))).strftime('%Y-%m-%d 00:00:00')

        startFrom = (page - 1) * page_size
        statement = """
            SELECT 
                SQL_CALC_FOUND_ROWS *
            FROM users
            WHERE 
                (latest_checkin_at IS NULL OR latest_checkin_at <= %s) AND 
                (latest_message_at IS NULL OR latest_message_at <= %s) AND 
                deleted_at IS NULL
            ORDER BY latest_checkin_at DESC, latest_message_at DESC, id ASC LIMIT %s OFFSET %s
        """
        parameters = (startAt, startAt, page_size, startFrom)
        cursor.execute(statement, parameters);
        result = cursor.fetchall();

        # 計算總頁數
        cursor.execute("SELECT FOUND_ROWS() as total_count");
        total_count = cursor.fetchone()['total_count'];

        return {
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'result': result
        }

    def getAllMemberPaginates(self, page: int = 1, page_size: int = 10):
        """
        getAllMemberPaginates 取得所有使用者的分頁資料

        :param page: 分頁頁碼，預設為 1
        :param page_size: 每頁顯示的資料數量，預設為 10
        :return: 包含總數量、當前頁碼、每頁大小和結果的字典
        例如：
        {
            'total_count': 100,
            'page': 1,
            'page_size': 10,
            'result': [
                {'id': 1, 'name': 'User1', ...},
                {'id': 2, 'name': 'User2', ...},
                ...
            ]
        }
        """
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        startFrom = (page - 1) * page_size
        statement = """
            SELECT 
                SQL_CALC_FOUND_ROWS *
            FROM users
            WHERE deleted_at IS NULL
            LIMIT %s OFFSET %s
        """
        parameters = (page_size, startFrom)
        cursor.execute(statement, parameters);
        result = cursor.fetchall();

        # 計算總頁數
        cursor.execute("SELECT FOUND_ROWS() as total_count");
        total_count = cursor.fetchone()['total_count'];

        return {
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'result': result
        }

    def undelete(self, uuid):
        """
        undelete 還原使用者資料 (SOFT UNDELETE)

        :param uuid: 使用者的 UUID
        :return: None
        """
        currentTimestamp = DatabaseConnection.getCurrentTimestamp();
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        statement = "UPDATE users SET deleted_at = NULL, updated_at = %s WHERE uuid = %s";
        cursor.execute(statement, (currentTimestamp, uuid,));
        connection.commit();
        return

    def delete(self, uuid):
        """
        delete 刪除使用者資 (SOFT DELETE)

        :param uuid: 使用者的 UUID
        :return: None
        """
        currentTimestamp = DatabaseConnection.getCurrentTimestamp();
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        statement = "UPDATE users SET deleted_at = %s WHERE uuid = %s";
        cursor.execute(statement, (currentTimestamp, uuid,));
        connection.commit();
        return

    def updateLastMessageAt(self, user: dict):
        """
        updateLastMessageAt 更新使用者的最後訊息時間

        :param user: 使用者物件
        :return: None
        """
        currentTimestamp = DatabaseConnection.getCurrentTimestamp();
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        statement = "UPDATE users SET latest_message_at = %s, updated_at = %s WHERE id = %s";
        cursor.execute(statement, (currentTimestamp, currentTimestamp, user['id'],));
        connection.commit();