from Services.DatabaseConnection import DatabaseConnection
class MerchandiseRepository:
    # 取得商品資料
    def findById(self, id):
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        statement = "SELECT merchandises.*, users.name AS user_name FROM merchandises LEFT JOIN users ON users.id = merchandises.user_id WHERE merchandises.id = %s AND deleted_at IS NULL"
        parameters = (id,);
        cursor.execute(statement, parameters);
        result = cursor.fetchone();

        return result;

    # 取得所有商品
    def getAll(self, user_id, page: int = 1, page_size: int = 10):
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        startFrom = (page - 1) * page_size
        statement = "SELECT SQL_CALC_FOUND_ROWS merchandises.*, users.name AS user_name FROM merchandises LEFT JOIN users ON users.id = merchandises.user_id WHERE deleted_at IS NULL "
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