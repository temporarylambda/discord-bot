from Repositories.GamblingDiceRepository import GamblingDiceRepository
from Services.TransferService import TransferService
from Enums.TransferReasonType import TransferReasonType
from Enums.TransferRelationType import TransferRelationType

class GamblingDiceService:
    def __init__(self) -> None:
        self.GamblingDiceRepository = GamblingDiceRepository()

    def insertRollRecord(self, Gambling: dict, User:dict, dices: list) -> None:
        """
        新增擲骰紀錄

        :param Gambling: 賭局資料
        :type Gambling: dict
        :param User: 使用者資料
        :type User: dict
        :param dices: 骰子列表
        :type dices: list
        :return: None
        :rtype: None
        """
        if not dices:
            raise ValueError("Dices cannot be empty")

        self.GamblingDiceRepository.upsert(Gambling["id"], User["id"], dices)