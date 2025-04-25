from Repositories.GamblerRepository import GamblerRepository

class GamblerService:
    def __init__(self) -> None:
        self.GamblerRepository = GamblerRepository()

    def get(self, Gambling: dict, User: dict) -> dict:
        """
        取得使用者在賭局中的資料

        :param Gambling: 賭局
        :type Gambling: dict
        :param User: 使用者
        :type User: dict
        :return: dict
        :rtype: dict
        """
        return self.GamblerRepository.get(Gambling['id'], User['id'])

    def join(self, Gambling: dict, User: dict) -> dict:
        """
        建立一筆賭局

        :param Gambling: 賭局
        :type Gambling: dict
        :param User: 使用者
        :type User: dict
        :return: dict
        :rtype: dict
        """
        return self.GamblerRepository.join(Gambling['id'], User['id'])