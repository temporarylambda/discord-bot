from Repositories.GamblingRepository import GamblingRepository
from Enums.GamblingType import GamblingType

class GamblingService:
    def __init__(self) -> None:
        self.GamblingRepository = GamblingRepository()

    def create(self, User: dict, min_bet: int, max_bet: int, type: GamblingType) -> dict:
        """
        建立一筆賭局

        :param User: 舉辦賭局的使用者資料
        :type User: dict
        :param min_bet: 最小賭注金額
        :type min_bet: int
        :param max_bet: 最大賭注金額
        :type max_bet: int
        :param type: GamblingType
        :type type: GamblingType
        :return: dict
        :rtype: dict
        """
        return self.GamblingRepository.create(
            user_id=User['id'], 
            min_bet=min_bet, 
            max_bet=max_bet, 
            type=type
        )