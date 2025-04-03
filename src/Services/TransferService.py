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

    # 給予簽到獎勵
    def giveCheckInReward(self, daily_check_in_topic_id, user, amount, note=None):
        reason = f"{user['name']} 簽到獎勵，金額 {amount} 元"
        transfer_reason_id = self.TransferReasonRepository.createCheckIn(reason=reason)
        self._transfer(transfer_reason_id=transfer_reason_id, user=user, amount=int(amount), fee=0, note=note)
        self._relation(transfer_reason_id, TransferRelationType.DAILY_CHECK_IN_TOPIC, [daily_check_in_topic_id])
        return;

    # 購買商品
    def buyMerchandise(self, from_user, to_user, merchandise, quantity=1):
        amount = int(merchandise['price']) * int(quantity)
        to_user_name = to_user['name'] if to_user is not None else "系統"
        reason = f"{from_user['name']} 購買商品 ID: {merchandise['id']}, {merchandise['name']} (by {to_user_name}) {quantity} 個，金額 {amount} 元"
        transfer_reason_id = self.TransferReasonRepository.createMerchandise(reason=reason)
        
        # trade_rate =  float(os.getenv("RULE_MERCHANDISE_TRADE_FEE", 0.2))
        # trade_fee  = int(amount * trade_rate)

        # 扣款不需要手續費
        self._transfer(transfer_reason_id=transfer_reason_id, user=from_user, amount=-amount, fee=0, note=reason)
        self._relation(transfer_reason_id, TransferRelationType.MERCHANDISE, [merchandise['id']])

        # 存入商品到使用者的背包
        inventoryIds = []
        for i in range(quantity):
            UserInventoryRepositoryObject = UserInventoryRepository()
            inventoryIds.append(UserInventoryRepositoryObject.addMerchandise(from_user['id'], merchandise))

        # 建立關聯
        self._relation(transfer_reason_id, TransferRelationType.INVENTORY, inventoryIds)
        return;

    # private method, 金額異動用
    def _transfer(self, transfer_reason_id, user, amount: int, fee: int =0, note=None):
        UserRepositoryObject = UserRepository();

        # 扣款 - 如果有指定 from_user，則代表這筆錢是從某個人身上扣除，沒有了話則是從系統扣除，紀錄一筆從系統扣除的轉帳紀錄
        self.TransferRecordRepository.create(transfer_reason_id, user['id'] if user is not None else None, amount, note)
        
        # 異動扣款對象餘額
        if user is not None:
            UserRepositoryObject.increaseBalance(user['id'], amount)

        # 手續費 - 若有手續費，則認定由系統收走
        if (fee and int(fee) > 0): 
            self.TransferRecordRepository.create(transfer_reason_id, None, fee, note)

        return;

    # private method, 紀錄轉帳關聯
    def _relation(self, transfer_reason_id, relation_type: TransferRelationType, relation_id: list = []):
        self.TransferReasonRepository.createRelation(transfer_reason_id, relation_type, relation_id)
        return;