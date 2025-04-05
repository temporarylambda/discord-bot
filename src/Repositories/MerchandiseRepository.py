from Services.DatabaseConnection import DatabaseConnection
class MerchandiseRepository:
    # 取得商品資料
    def findById(self, id):
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        statement = "SELECT merchandises.*, users.name AS user_name, users.uuid FROM merchandises LEFT JOIN users ON users.id = merchandises.user_id WHERE merchandises.id = %s AND deleted_at IS NULL"
        parameters = (id,);
        cursor.execute(statement, parameters);
        result = cursor.fetchone();

        return result;

    def getAll(self, user_id = None):
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        statement = """
            SELECT 
                merchandises.*, 
                users.name AS user_name,
                users.uuid 
            FROM merchandises 
            LEFT JOIN users ON users.id = merchandises.user_id 
            WHERE deleted_at IS NULL 
        """
        if (user_id is not None):
            statement += "AND merchandises.user_id = %s "
        parameters = (user_id,) if user_id is not None else ();
        cursor.execute(statement, parameters);
        result = cursor.fetchall();

        return result;

    # 取得所有商品
    def getAllPaginates(self, user_id, page: int = 1, page_size: int = 10):
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        startFrom = (page - 1) * page_size
        statement = """
            SELECT 
                SQL_CALC_FOUND_ROWS 
                merchandises.*, 
                users.name AS user_name,
                users.uuid 
            FROM merchandises 
            LEFT JOIN users ON users.id = merchandises.user_id 
            WHERE deleted_at IS NULL 
        """
        if (user_id is not None):
            statement += "AND merchandises.user_id = %s "
        statement += "LIMIT %s OFFSET %s"
        parameters = (page_size, startFrom) if user_id is None else (user_id, page_size, startFrom);
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

    # 新增商品
    def create(self, user_id, merchandise):
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);
        currentTimestamp = DatabaseConnection.getCurrentTimestamp();

        statement = "INSERT INTO merchandises (user_id, name, description, price, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)"
        parameters = (user_id, merchandise['name'], merchandise['description'], merchandise['price'], currentTimestamp, currentTimestamp);
        cursor.execute(statement, parameters);
        connection.commit();

        return cursor.lastrowid;

    # 下架商品
    def delete(self, ids: list = []):
        print(ids)
        if len(ids) == 0:
            return 0 # 如果沒有傳入 ids，則不進行任何操作

        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()

        placeholders = ', '.join(['%s'] * len(ids))  # 根據 ids 數量產生 %s
        statement = f"""
            UPDATE merchandises
            SET deleted_at = %s
            WHERE id IN ({placeholders}) AND deleted_at IS NULL
        """
        parameters = [currentTimestamp] + ids  # 將 currentTimestamp 與 ids 合併為一個參數列表
        cursor.execute(statement, parameters)
        connection.commit()

        return cursor.rowcount
