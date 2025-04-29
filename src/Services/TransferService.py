import os
from Repositories.TransferRecordRepository import TransferRecordRepository 
from Repositories.TransferReasonRepository import TransferReasonRepository
from Repositories.UserRepository import UserRepository
from Repositories.UserInventoryRepository import UserInventoryRepository
from Repositories.DailyCheckInTopicRepository import DailyCheckInTopicRepository
from Enums.TransferRelationType import TransferRelationType
from Enums.MerchandiseSystemType import MerchandiseSystemType
from Enums.TransferReasonType import TransferReasonType

class TransferService:
    # 購買商品
    def buyMerchandise(self, from_user, to_user, merchandise, quantity=1):
        amount = int(merchandise['price']) * int(quantity)
        to_user_name = to_user['name'] if to_user is not None else "系統"

        # 存入商品到使用者的背包
        inventoryIds = []
        for i in range(quantity):
            UserInventoryRepositoryObject = UserInventoryRepository()
            inventoryIds.append(UserInventoryRepositoryObject.addMerchandise(from_user['id'], merchandise))

        # 扣款
        self.transfer(
            FromUser=from_user,
            ToUser=None,
            amount=amount,
            reason=f"{from_user['name']} 購買商品 ID: {merchandise['id']}, {merchandise['name']} (by {to_user_name}) {quantity} 個，金額 {amount} 元",
            transfer_type=TransferReasonType.MERCHANDISE,
            relation_dict=[
                {
                    'type': TransferRelationType.MERCHANDISE,
                    'id': [merchandise['id']]
                },
                {
                    'type': TransferRelationType.INVENTORY,
                    'id': inventoryIds
                }
            ]
        )
        return

    # 兌換商品 - 如果兌換的商品是任務刷新卷，則需要傳入 dailyCheckInTopicIds, 並將這些題目標記為已跳過
    def redeemMerchandise(self, User, Inventory, dailyCheckInTopicIds: list = []):
        amount = int(Inventory['price'])
        fee = int(amount * float(os.getenv("RULE_MERCHANDISE_TRADE_FEE", 0.2)))
        to_user_name = Inventory['merchant_name'] if Inventory['merchant_name'] is not None else "系統"
        relation_dict = [{'type': TransferRelationType.INVENTORY, 'id': [Inventory['id']]}]

         # 任務刷新卷
        DailyCheckInTopicRepositoryObject = DailyCheckInTopicRepository()
        if Inventory['system_type'] == MerchandiseSystemType.SYSTEM_CHECK_IN_REFRESH.value:
            relation_dict.append({'type': TransferRelationType.DAILY_CHECK_IN_TOPIC, 'id': dailyCheckInTopicIds}) # 紀錄關聯的 Topic Ids
            for daily_check_in_topic_id in dailyCheckInTopicIds: # 將這些題目標記為已跳過
                DailyCheckInTopicRepositoryObject.skip(daily_check_in_topic_id)

        self.transfer(
            FromUser=None,
            ToUser={'id': Inventory['merchant_id']},
            amount=amount,
            fee=int(amount * float(os.getenv("RULE_MERCHANDISE_TRADE_FEE", 0.2))),
            reason=f"{User['name']} 兌換商品 ID: {Inventory['merchandise_id']}, {Inventory['name']} (by {to_user_name}) 1 個，原價 {Inventory['price']} 元，手續費 {fee} 元，實際兌換金額 {amount} 元",
            transfer_type=TransferReasonType.REDEEM,
            relation_dict=relation_dict
        )

        return {
            'price': amount,
            'fee': fee,
            'final_price': amount - fee,
        }

    def transfer(
        self, 
        ToUser: dict, 
        FromUser: dict, 
        amount: int, 
        reason: str = None, 
        fee: int = 0, 
        transfer_type: TransferReasonType = TransferReasonType.TRANSFER,
        relation_dict: list = []
    ) -> dict:
        """
        產生轉帳紀錄

        :param ToUser: 轉入對象, 如果是系統方，則給予 None
        :type ToUser: dict or None
        :param FromUser: 轉出對象, 如果是系統方，則給予 None
        :type FromUser: dict or None
        :param amount: 轉帳金額
        :type amount: int
        :param reason: 轉帳原因
        :type reason: str
        :param fee: 手續費
        :type fee: int
        :param transfer_type: 轉帳類型
        :type transfer_type: TransferReasonType
        :param relation_dict: 轉帳關聯字典
        :type relation_dict: list
        :param relation_type: 轉帳關聯類型 - DEPRECATED, 請改用 relation_dict
        :type relation_type: TransferRelationType
        :param relation_id: 轉帳關聯ID - DEPRECATED, 請改用 relation_dict
        :type relation_id: list
        :return dict
        """
        response = {'amount': int(amount), 'fee': int(fee), 'transfer_reason_id': None}
        if (amount is None or int(amount) <= 0):
            return response

        TransferReasonRepositoryObject = TransferReasonRepository()
        TransferRecordRepositoryObject = TransferRecordRepository()
        UserRepositoryObject = UserRepository()

        toUserAmount        = int(amount) - int(fee)
        fromUserAmount      = -int(amount)
        ToUserId            = ToUser.get('id', None) if ToUser is not None else None
        FromUserId          = FromUser.get('id', None) if FromUser is not None else None
        transfer_reason_id  = TransferReasonRepositoryObject.create(type=transfer_type, reason=reason)

        # 建立轉帳紀錄 - ToUser
        TransferRecordRepositoryObject.create(transfer_reason_id, ToUserId, toUserAmount, note=reason)
        UserRepositoryObject.increaseBalance(ToUserId, toUserAmount)

        # 建立轉帳紀錄 - FromUser
        TransferRecordRepositoryObject.create(transfer_reason_id, FromUserId, fromUserAmount, note=reason)
        UserRepositoryObject.increaseBalance(FromUserId, fromUserAmount)

        # 手續費
        if (fee and int(fee) > 0):
            TransferRecordRepositoryObject.create(transfer_reason_id, None, fee, reason)

        # 設定關聯
        for relation in relation_dict:
            if relation.get('type') and relation.get('id'):
                TransferReasonRepositoryObject.createRelation(transfer_reason_id, relation.get('type'), relation.get('id'))

        response['transfer_reason_id'] = transfer_reason_id
        return response