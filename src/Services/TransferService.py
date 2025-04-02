from Repositories.TransferRecordRepository import TransferRecordRepository 
from Repositories.TransferReasonRepository import TransferReasonRepository
from Repositories.UserRepository import UserRepository
class TransferService:
    def __init__(self):
        self.TransferReasonRepository = TransferReasonRepository();
        self.TransferRecordRepository = TransferRecordRepository();

    # 玩家雙方轉帳
    def transfer(self, from_user, to_user, amount, fee=15, note=None):
        reason = f"{from_user['name']} 轉帳給 {to_user['name']}，金額 {amount} 元，手續費 {fee} 元"
        reason_id = self.TransferReasonRepository.createTransfer(reason=reason)

        self._transfer(reason_id=reason_id, to_user=to_user, amount=int(amount), fee=int(fee), note=note, from_user=from_user)
        return

    # 給予簽到獎勵
    def giveCheckInReward(self, daily_check_in_topic_id, to_user, amount, note=None):
        reason = f"{to_user['name']} 簽到獎勵，金額 {amount} 元"
        reason_id = self.TransferReasonRepository.createCheckIn(reason=reason, item_id=daily_check_in_topic_id)
        self._transfer(reason_id=reason_id, to_user=to_user, amount=int(amount), fee=0, note=note)
        return;

        return;

    # private method, 金額異動用
    def _transfer(self, reason_id, to_user, amount: int, fee: int =0, note=None, from_user=None):
        UserRepositoryObject = UserRepository();

        # 扣款 - 如果有指定 from_user，則代表這筆錢是從某個人身上扣除，沒有了話則是從系統扣除，紀錄一筆從系統扣除的轉帳紀錄
        self.TransferRecordRepository.create(reason_id, from_user['id'] if from_user is not None else None, -amount, note)
        
        # 異動扣款對象餘額
        if from_user is not None:
            UserRepositoryObject.increaseBalance(from_user['id'], amount)

        # 撥款
        self.TransferRecordRepository.create(reason_id, to_user['id'], amount - fee, note)
        
        # 異動撥款對象餘額
        if to_user is not None:
            UserRepositoryObject.increaseBalance(to_user['id'], amount - fee)

        # 手續費 - 若有手續費，則認定由系統收走
        if (fee and int(fee) > 0): 
            self.TransferRecordRepository.create(reason_id, None, fee, note)

        return;