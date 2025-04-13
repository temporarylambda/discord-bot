from enum import Enum
class GamblerStatus(Enum):
    """
    參與者狀態
    """
    # 參與者狀態
    PENDING = 'PENDING' # 等候開始
    GAMBLING = 'GAMBLING' # 賭局中
    LOSER = 'LOSER' # 輸家
    WINNER = 'WINNER' # 贏家
    ABSTAIN = 'ABSTAIN' # 棄權者(等同輸家)