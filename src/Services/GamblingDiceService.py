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

    def ranking(self, Gambling: dict, sort_order: str = "DESC", limit: int = 1) -> list:
        """
        取得賭局的擲骰紀錄

        :param Gambling: 賭局資料
        :type Gambling: dict
        :param sort_order: 排序方式，預設為 DESC
        :type sort_order: str
        :param limit: 取得排名的人數，預設為 1
        :type limit: int
        :return: 擲骰紀錄列表
        :rtype: list
        """
        return self.GamblingDiceRepository.ranking(gambling_id=Gambling["id"], limit=limit, sort_order=sort_order)