from enum import Enum
class TransferRelationType(Enum):
    # 商品
    MERCHANDISE = 'MERCHANDISE'

    # 使用者庫存
    INVENTORY = 'INVENTORY'

    # 簽到 Topic
    DAILY_CHECK_IN_TOPIC = 'DAILY_CHECK_IN_TOPIC'

    # 賭博
    GAMBLING = 'GAMBLING'