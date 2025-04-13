import os
from Repositories.GamblingRepository import GamblingRepository
from Repositories.GamblerRepository import GamblerRepository
from Repositories.TransferReasonRepository import TransferReasonRepository
from Repositories.TransferRecordRepository import TransferRecordRepository
from Enums.GamblingType import GamblingType
from Enums.TransferReasonType import TransferReasonType
from Enums.TransferRelationType import TransferRelationType
from Enums.GamblingStatus import GamblingStatus
from Exceptions.GamblingException import GamblingException

class GamblingService:
    def __init__(self, *args, **kwargs):
        self.GamblingRepository = GamblingRepository()
        self.GamblerRepository  = GamblerRepository()
        self.TransferReasonRepository = TransferReasonRepository()
        self.TransferRecordRepository = TransferRecordRepository()

    def host(self, User: dict, type: GamblingType, amount: int) -> dict:
        """
        主持賭局
        :param User: 使用者資訊 (users table)
        :param type: 賭局類型
        :param amount: 賭金
        :return: gambling.*
        """

        # 檢查是否擁有足夠的金額
        if int(User['balance']) < int(amount):
            raise GamblingException.NOT_ENOUGH_MONEY(amount, User['balance'])

        Gambling = self.GamblingRepository.create(User['id'], type, amount, amount)
        self.join(User, Gambling)
        return Gambling
    
    def join(self, User: dict, Gambling: dict | int) -> int:
        """
        參加賭局

        :param User: 使用者資訊 (users table)
        :param Gambling: 賭局資訊 (gambling table)
        :return: gambler.id
        """
        Gambling = self.GamblerRepository.findById(Gambling) if not isinstance(Gambling, dict) else Gambling

        # 檢查是否擁有足夠的金額
        if int(User['balance']) < int(Gambling['min_bet']):
            raise GamblingException.NOT_ENOUGH_MONEY(Gambling['min_bet'], User['balance'])

        # 將金錢轉至賭局
        description = f"{User['name']} 下注金額 {Gambling['min_bet']} 元 - 參與賭局 (gambling_id: {Gambling['id']})"
        transfer_reason_id = self.TransferReasonRepository.create(TransferReasonType.BET, description)
        self.TransferRecordRepository.transfer(transfer_reason_id=transfer_reason_id, user_id=User['id'], amount=-int(Gambling['min_bet']), fee=0, note=description)
        self.TransferRecordRepository.transfer(transfer_reason_id=transfer_reason_id, user_id=None, amount=int(Gambling['min_bet']), fee=0, note=description)
        self.TransferReasonRepository.createRelation(transfer_reason_id=transfer_reason_id, relation_type=TransferRelationType.GAMBLING, relation_ids=[Gambling['id']])

        # 標記參與賭局
        joinId = self.GamblerRepository.join(user_id=User['id'], gambling_id=Gambling['id'])

        # 更新參與者賭金
        self.GamblerRepository.raiseBet(user_id=User['id'], gambling_id=Gambling['id'], amount=int(Gambling['min_bet']))
        return joinId

    def exit(self, User: dict, Gambling: dict | int) -> dict:
        """
        退出賭局

        :param User: 使用者資訊 (users table)
        :param Gambling: 賭局資訊 (gambling table)
        :return: gambler.id
        """
        Gambling = self.GamblerRepository.findById(Gambling) if not isinstance(Gambling, dict) else Gambling
        isRefund = (Gambling['status'] == GamblingStatus.PENDING.value) # 如果尚未開始賭局，就可以退款

        JoinRecord = self.GamblerRepository.findById(Gambling['id'], User['id'])

        if (isRefund):
            description = f"{User['name']} 退出賭局，由於賭局尚未開始故返回下注金額 {Gambling['min_bet']} 元 - 參與賭局 (gambling_id: {Gambling['id']})"
            transfer_reason_id = self.TransferReasonRepository.create(TransferReasonType.BET, description)
            self.TransferRecordRepository.transfer(transfer_reason_id=transfer_reason_id, user_id=User['id'], amount=-int(Gambling['min_bet']), fee=0, note=description)
            self.TransferRecordRepository.transfer(transfer_reason_id=transfer_reason_id, user_id=None, amount=int(Gambling['min_bet']), fee=0, note=description)
            self.TransferReasonRepository.createRelation(transfer_reason_id=transfer_reason_id, relation_type=TransferRelationType.GAMBLING, relation_ids=[Gambling['id']])
        

        # 標記參與賭局
        self.GamblerRepository.exit(user_id=User['id'], gambling_id=Gambling['id'])
