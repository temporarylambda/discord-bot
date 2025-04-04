from Enums.UserInventoryStatus import UserInventoryStatus
from Services.DatabaseConnection import DatabaseConnection
from typing import Optional
class UserInventoryRepository:
    # 取得使用者的所有商品 - 相同商品會合併統計數量
    def getAll(self, user_id, page: int = 1, page_size: Optional[int] = 10):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        statement = """
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
        """
        parameters = [user_id, UserInventoryStatus.PENDING.value]
        if (page_size is not None):
            statement += " LIMIT %s OFFSET %s"
            parameters.append(page_size)
            parameters.append((page - 1) * page_size)

        cursor.execute(statement, parameters)
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

    # 給予使用者指定商品
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

    # 取得使用者指定商品類型中的第一個物品
    def firstByMerchandiseId(self, user_id, merchandise_id):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        cursor.execute(
            """
                SELECT 
                    user_inventories.*,
                    merchandises.id AS merchandise_id,
                    merchandises.name, 
                    merchandises.description,
                    merchandises.price,
                    merchandises.user_id AS merchant_id,
                    merchandises.system_type,
                    users.name AS merchant_name,
                    users.uuid AS merchant_uuid
                FROM user_inventories 
                INNER JOIN merchandises ON merchandises.id = user_inventories.merchandise_id
                LEFT JOIN users ON users.id = merchandises.user_id
                WHERE user_inventories.user_id = %s AND merchandise_id = %s AND status = %s
                ORDER BY user_inventories.created_at ASC, user_inventories.id ASC
            """,
            (user_id, merchandise_id, UserInventoryStatus.PENDING.value)
        )
        return cursor.fetchone()

    # 兌換商品
    def redeem(self, inventory_id):
        connection = DatabaseConnection.connect()
        cursor = DatabaseConnection.cursor(connection)
        currentTimestamp = DatabaseConnection.getCurrentTimestamp()
        cursor.execute(
            "UPDATE user_inventories SET status = %s, redeemed_at = %s, updated_at = %s WHERE id = %s",
            (UserInventoryStatus.REDEEMED.value, currentTimestamp, currentTimestamp, inventory_id)
        )
        connection.commit()
        return cursor.rowcount