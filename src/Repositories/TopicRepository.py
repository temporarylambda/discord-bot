from Services.DatabaseConnection import DatabaseConnection

class TopicRepository:
    # 隨機取得一條題目
    def random(self):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute("SELECT * FROM topics WHERE deleted_at IS NULL ORDER BY RAND() LIMIT 1")
        row = cursor.fetchone()
        return row

    # 取得所有題目
    def create(self, topic: dict):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        cursor.execute(
            "INSERT INTO topics (description, reward, note, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)", 
            (topic['description'], topic['reward'], topic['note'], currentTimestamp, currentTimestamp)
        )
        connection.commit()
        return cursor.lastrowid

    # 取得所有商品
    def getAllPaginates(self, page: int = 1, page_size: int = 10):
        connection = DatabaseConnection.connect();
        cursor = DatabaseConnection.cursor(connection);

        startFrom  = (page - 1) * page_size
        statement  = "SELECT SQL_CALC_FOUND_ROWS topics.* FROM topics WHERE deleted_at IS NULL "
        statement += "LIMIT %s OFFSET %s"
        cursor.execute(statement, (page_size, startFrom));
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

    # 任務下架
    def delete(self, ids: list = []):
        if len(ids) == 0:
            return

        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()

        placeholders = ', '.join(['%s'] * len(ids))  # 生成正確的佔位符數量
        sql = f"UPDATE topics SET deleted_at = %s, updated_at = %s WHERE id IN ({placeholders})"
        params = [currentTimestamp, currentTimestamp] + ids           # 合併參數順序

        cursor.execute(sql, params)
        connection.commit()

        return cursor.rowcount

    def findById(self, id: int):
        if id is None:
            return None

        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute("SELECT * FROM topics WHERE id = %s AND deleted_at IS NULL", (id,))
        row = cursor.fetchone()
        return row