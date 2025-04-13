from enum import Enum
class GamblingStatus(Enum):
    PENDING  = 'PENDING'    # 待開始
    GAMBLING = 'GAMBLING'   # 進行中
    CANCELED = 'CANCELED'   # 已取消
    FINISHED = 'FINISHED'   # 已結束
