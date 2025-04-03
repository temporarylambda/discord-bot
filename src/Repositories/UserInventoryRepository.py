from Enums.UserInventoryStatus import UserInventoryStatus
from Services.DatabaseConnection import DatabaseConnection
class UserInventoryRepository:
    # 取得使用者的所有商品 - 相同商品會合併統計數量
    def getAll(self, user_id, page: int = 1, page_size: int = 10):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            """
                SELECT SQL_CALC_FOUND_ROWS
                    `merchandises`.`id` AS `merchandise_id`,
                    `merchandises`.`user_id` AS `merchant_id`,
                    `users`.`name` AS `merchant_name`,
                    `merchandises`.`name`,
                    COUNT(`user_inventories`.`id`) AS `quantity`
                FROM `user_inventories`
                INNER JOIN `merchandises` ON `merchandises`.`id` = `user_inventories`.`merchandise_id`
                LEFT JOIN `users` ON `users`.`id` = `merchandises`.`user_id`
                WHERE `user_inventories`.`user_id` = %s AND `user_inventories`.`status` = %s
                GROUP BY `merchandises`.`id`
                ORDER BY COUNT(`user_inventories`.`id`) DESC
                LIMIT %s OFFSET %s
            """, 
            (user_id, UserInventoryStatus.PENDING.value, page_size, (page - 1) * page_size)
        )
        result = cursor.fetchall()

        # 計算總頁數
        cursor.execute("SELECT FOUND_ROWS() as total_count")
        total_count = cursor.fetchone()['total_count']

        return {
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'result': result
        }
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