import os
from Repositories.TransferRecordRepository import TransferRecordRepository 
from Repositories.TransferReasonRepository import TransferReasonRepository
from Repositories.UserRepository import UserRepository
from Repositories.UserInventoryRepository import UserInventoryRepository
from Enums.TransferRelationType import TransferRelationType
class TransferService:
    def __init__(self):
        self.TransferReasonRepository = TransferReasonRepository();
        self.TransferRecordRepository = TransferRecordRepository();
        self.UserRepository = UserRepository();

    # 給予簽到獎勵
    def giveCheckInReward(self, daily_check_in_topic_id, user, amount, note=None):
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

    def redeemMerchandise(self, User, Inventory):
        amount = int(Inventory['price'])
        fee = int(amount * float(os.getenv("RULE_MERCHANDISE_TRADE_FEE", 0.2)))

        to_user_name = Inventory['merchant_name'] if Inventory['merchant_name'] is not None else "系統"
        reason = f"{User['name']} 兌換商品 ID: {Inventory['merchandise_id']}, {Inventory['name']} (by {to_user_name}) 1 個，原價 {Inventory['price']} 元，手續費 {fee} 元，實際兌換金額 {amount} 元"
        transfer_reason_id = self.TransferReasonRepository.createRedeem(reason=reason)
        self._transfer(transfer_reason_id=transfer_reason_id, user_id=Inventory['merchant_id'], amount=amount-fee, fee=fee, note=reason)
        self._relation(transfer_reason_id, TransferRelationType.INVENTORY, [Inventory['id']])
        return {
            'price': amount,
            'fee': fee,
            'final_price': amount - fee,
        }

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