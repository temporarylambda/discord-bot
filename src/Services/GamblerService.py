from Repositories.GamblerRepository import GamblerRepository
from Services.TransferService import TransferService
from Enums.TransferReasonType import TransferReasonType
from Enums.TransferRelationType import TransferRelationType

class GamblerService:
    def __init__(self) -> None:
        self.GamblerRepository = GamblerRepository()
        self.TransferService = TransferService() # 為了節省程式碼，將 TransferService 的實例化放在這裡

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

    def join(self, Gambling: dict, User: dict, bet: int) -> dict:
        """
        加入賭局

        :param Gambling: 賭局
        :type Gambling: dict
        :param User: 使用者
        :type User: dict
        :param bet: 賭注金額
        :type bet: int
        :return: dict
        :rtype: dict
        """
        result = self.GamblerRepository.join(Gambling['id'], User['id'])
        self.raiseBet(Gambling, User, bet)
        return result
    
    def raiseBet(self, Gambling: dict, User: dict, bet: int) -> dict:
        """
        提高賭注金額

        :param Gambling: 賭局
        :type Gambling: dict
        :param User: 使用者
        :type User: dict
        :param bet: 賭注金額
        :type bet: int
        :return: dict
        :rtype: dict
        """
        result = self.GamblerRepository.raiseBet(Gambling['id'], User['id'], bet)
        reason = "開啟賭局" if Gambling['user_id'] == User['id'] else "參加賭局"
        self.TransferService.transfer(
            FromUser=User, 
            ToUser=None, 
            amount=bet, 
            fee=0, 
            reason=f"{reason} - 賭局編號: {Gambling['id']}", 
            transfer_type=TransferReasonType.BET_IN,
            relation_dict=[
                {
                    'type': TransferRelationType.GAMBLING,
                    'id': [Gambling['id']]
                }
            ]
        )
        return result
    
    def cancel(self, Gambling: dict, User: dict, isHostForceCancel: bool = False) -> dict:
        """
        取消參加賭局

        :param Gambling: 賭局
        :type Gambling: dict
        :param User: 使用者
        :type User: dict
        :return: dict
        :rtype: dict
        """
        result = self.GamblerRepository.cancel(Gambling['id'], User['id'])
        reason  = "退款 - "
        reason += "主持人離開" if isHostForceCancel else "玩家退出"
        reason += f" - 賭局編號: {Gambling['id']}"

        player = self.GamblerRepository.get(Gambling['id'], User['id'])
        self.TransferService.transfer(
            FromUser=None, 
            ToUser=User, 
            amount=int(player['total_bets']), 
            fee=0, 
            reason=reason, 
            transfer_type=TransferReasonType.BET_REFOUND,
            relation_dict=[
                {
                    'type': TransferRelationType.GAMBLING,
                    'id': [Gambling['id']]
                }
            ]
        )
        return result

    def start(self, Gambling: dict) -> dict:
        """
        開始賭局

        :param Gambling: 賭局
        :type Gambling: dict
        :return: dict
        :rtype: dict
        """
        return self.GamblerRepository.start(Gambling['id'])

    def settle(self, Gambling: dict, Users: list[dict]) -> None:
        """
        結算賭局結果

        - 標記贏家
        - 轉帳贏家賭金
        - 轉帳給贏家

        :param Gambling: 賭局
        :type Gambling: dict
        :param Users: 贏家
        :type Users: list[dict]
        :return: None
        """

        # 標記贏家
        user_ids = [User['id'] for User in Users]
        self.GamblerRepository.setWinner(Gambling['id'], user_ids)

        # 取的賭局總金額
        totalBets = self.GamblerRepository.getTotalBets(Gambling['id'])
        for User in Users:
            # 轉帳給贏家
            self.TransferService.transfer(
                FromUser=None, 
                ToUser=User, 
                amount=int(totalBets/len(Users)), # 如果有多位贏家，則平均分配賭金；如果賭金不該能被整除，那多給的錢就當作系統送的
                fee=0, 
                reason=f"賭局贏家 - 賭局編號: {Gambling['id']}", 
                transfer_type=TransferReasonType.BET_WIN,
                relation_dict=[
                    {
                        'type': TransferRelationType.GAMBLING,
                        'id': [Gambling['id']]
                    }
                ]
            )
        return