import os
from Repositories.TransferRecordRepository import TransferRecordRepository 
from Repositories.TransferReasonRepository import TransferReasonRepository
from Repositories.UserRepository import UserRepository
from Repositories.UserInventoryRepository import UserInventoryRepository
from Repositories.DailyCheckInTopicRepository import DailyCheckInTopicRepository
from Enums.TransferRelationType import TransferRelationType
from Enums.MerchandiseSystemType import MerchandiseSystemType
class TransferService:
    def __init__(self):
        self.TransferReasonRepository = TransferReasonRepository();
        self.TransferRecordRepository = TransferRecordRepository();
        self.DailyCheckInTopicRepository = DailyCheckInTopicRepository();
        self.UserRepository = UserRepository();

    # 給予簽到獎勵
    def giveCheckInReward(self, daily_check_in_topic_id, user, amount, note=None):
        if (amount is None or int(amount) <= 0):
            return

        reason = f"{user['name']} 簽到獎勵 (DailyCheckInTopicId: {daily_check_in_topic_id})，金額 {amount} 元"
        transfer_reason_id = self.TransferReasonRepository.createCheckIn(reason=reason)
        self._transfer(transfer_reason_id=transfer_reason_id, user_id=user['id'], amount=int(amount), fee=0, note=reason)
        self._relation(transfer_reason_id, TransferRelationType.DAILY_CHECK_IN_TOPIC, [daily_check_in_topic_id])
        return;

    # 購買商品
    def buyMerchandise(self, from_user, to_user, merchandise, quantity=1):
        amount = int(merchandise['price']) * int(quantity)
        to_user_name = to_user['name'] if to_user is not None else "系統"
        reason = f"{from_user['name']} 購買商品 ID: {merchandise['id']}, {merchandise['name']} (by {to_user_name}) {quantity} 個，金額 {amount} 元"
        transfer_reason_id = self.TransferReasonRepository.createMerchandise(reason=reason)

        # 扣款不需要手續費
        self._transfer(transfer_reason_id=transfer_reason_id, user_id=from_user['id'], amount=-amount, fee=0, note=reason)
        self._relation(transfer_reason_id, TransferRelationType.MERCHANDISE, [merchandise['id']])

        # 存入商品到使用者的背包
        inventoryIds = []
        for i in range(quantity):
            UserInventoryRepositoryObject = UserInventoryRepository()
            inventoryIds.append(UserInventoryRepositoryObject.addMerchandise(from_user['id'], merchandise))

        # 建立關聯
        self._relation(transfer_reason_id, TransferRelationType.INVENTORY, inventoryIds)
        return;

    # 兌換商品 - 如果兌換的商品是任務刷新卷，則需要傳入 dailyCheckInTopicIds, 並將這些題目標記為已跳過
    def redeemMerchandise(self, User, Inventory, dailyCheckInTopicIds: list = []):
        amount = int(Inventory['price'])
        fee = int(amount * float(os.getenv("RULE_MERCHANDISE_TRADE_FEE", 0.2)))

        to_user_name = Inventory['merchant_name'] if Inventory['merchant_name'] is not None else "系統"
        reason = f"{User['name']} 兌換商品 ID: {Inventory['merchandise_id']}, {Inventory['name']} (by {to_user_name}) 1 個，原價 {Inventory['price']} 元，手續費 {fee} 元，實際兌換金額 {amount} 元"
        transfer_reason_id = self.TransferReasonRepository.createRedeem(reason=reason)
        self._transfer(transfer_reason_id=transfer_reason_id, user_id=Inventory['merchant_id'], amount=amount-fee, fee=fee, note=reason)
        self._relation(transfer_reason_id, TransferRelationType.INVENTORY, [Inventory['id']])

        # 任務刷新卷
        if Inventory['system_type'] == MerchandiseSystemType.SYSTEM_CHECK_IN_REFRESH.value:
            # 紀錄關聯的 Topic Ids
            self._relation(transfer_reason_id, TransferRelationType.DAILY_CHECK_IN_TOPIC, dailyCheckInTopicIds)

            # 將這些題目標記為已跳過
            for daily_check_in_topic_id in dailyCheckInTopicIds:
                self.DailyCheckInTopicRepository.skip(daily_check_in_topic_id);

        return {
            'price': amount,
            'fee': fee,
            'final_price': amount - fee,
        }

    # 轉帳
    def transfer(self, FromUser, ToUser, amount):
        transferFee = os.getenv("RULE_TRANSFER_FEE", 15)
        reason = f"{FromUser['name']} 轉帳給 {ToUser['name']}，金額 {amount} 元，手續費 {transferFee} 元"
        transfer_reason_id = self.TransferReasonRepository.createTransfer(reason=reason)

        increaseAmount = int(amount)
        decreesAmount  = int(amount) + int(transferFee)
        self._transfer(transfer_reason_id=transfer_reason_id, user_id=FromUser['id'], amount=-decreesAmount, fee=transferFee, note=reason)
        self._transfer(transfer_reason_id=transfer_reason_id, user_id=ToUser['id'], amount=increaseAmount, note=reason)
        return {
            'amount': amount,
            'fee': transferFee,
            'final_amount': amount,
        };

    # 管理方撥款給指定成員
    def giveMoney(self, AdminUser, User, amount, note=None):
        reason = note if note is not None else f"{AdminUser['name']} 給予 {User['name']} 金額 {amount} 元"
        transfer_reason_id = self.TransferReasonRepository.createGive(reason=reason)
        self._transfer(transfer_reason_id=transfer_reason_id, user_id=User['id'], amount=int(amount), fee=0, note=reason)
        return;

    # 管理方強制從指定成員扣款
    def takeMoney(self, AdminUser: dict, User: dict, amount, note=None):
        reason = note if note is not None else f"{AdminUser['name']} 扣除 {User['name']} 金額 {amount} 元"
        transfer_reason_id = self.TransferReasonRepository.createTake(reason=reason)
        self._transfer(transfer_reason_id=transfer_reason_id, user_id=User['id'], amount=-int(amount), fee=0, note=reason)
        return;

    # private method, 金額異動用
    def _transfer(self, transfer_reason_id, user_id, amount: int, fee: int =0, note=None):
        # 轉帳紀錄
        self.TransferRecordRepository.create(transfer_reason_id, user_id if user_id is not None else None, amount, note)
        
        # 異動扣款對象餘額 - 如果 user_id 為 None，則代表是對系統方的計算，這情況下不需異動 users 餘額，因為沒有對應的 record
        if user_id is not None:
            self.UserRepository.increaseBalance(user_id, amount)

        # 手續費 - 若有手續費，則認定由系統收走
        if (fee and int(fee) > 0): 
            self.TransferRecordRepository.create(transfer_reason_id, None, fee, note)

        return;

    # private method, 紀錄轉帳關聯
    def _relation(self, transfer_reason_id, relation_type: TransferRelationType, relation_id: list = []):
        self.TransferReasonRepository.createRelation(transfer_reason_id, relation_type, relation_id)
        return;