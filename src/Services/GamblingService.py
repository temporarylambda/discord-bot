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

    def start(self, Gambling: dict) -> dict:
        """
        開始賭局

        :param Gambling: 賭局資料
        :type Gambling: dict
        :return: dict
        :rtype: dict
        """
        return self.GamblingRepository.start(Gambling['id'])
    
    def cancel(self, Gambling: dict) -> dict:
        """
        取消賭局

        :param Gambling: 賭局資料
        :type Gambling: dict
        :return: dict
        :rtype: dict
        """
        return self.GamblingRepository.cancel(Gambling['id'])
    
    def finish(self, Gambling: dict) -> dict:
        """
        結束賭局

        :param Gambling: 賭局資料
        :type Gambling: dict
        :return: dict
        :rtype: dict
        """
        return self.GamblingRepository.finish(Gambling['id'])
