from enum import Enum
class GamblerStatus(Enum):
    """
    賭局參加者狀態

    :param PENDING: 等待遊戲開始中
    :type PENDING: str

    :param IN_PROGRESS: 遊戲中
    :type IN_PROGRESS: str

    :param WINNER: 贏家
    :type WINNER: str

    :param LOSER: 輸家
    :type LOSER: str

    :param CANCELED: 取消參加
    :type CANCELED: str
    """
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    WINNER = "WINNER"
    LOSER = "LOSER"
    CANCELED = "CANCELED"