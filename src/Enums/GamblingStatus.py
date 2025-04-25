from enum import Enum
class GamblingStatus(Enum):
    """
    賭局狀態

    :param PENDING: 等待中
    :type PENDING: str

    :param IN_PROGRESS: 進行中
    :type IN_PROGRESS: str

    :param FINISHED: 已結束
    :type FINISHED: str

    :param CANCELED: 已取消
    :type CANCELED: str
    """
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    FINISHED = 'FINISHED'
    CANCELED = 'CANCELED'