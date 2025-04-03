from enum import Enum
class TransferReasonType(Enum):
    # 玩家彼此轉帳
    TRANSFER = 'TRANSFER'

    # 系統發放金錢
    GIVE = 'GIVE'

    # 系統扣除金錢
    TAKE = 'TAKE'

    # 購買商品
    MERCHANDISE = 'MERCHANDISE'

    # 簽到獎勵發放
    CHECK_IN = 'CHECK_IN'

    # 退款
    REFUND = 'REFUND'

    # 消費者兌換商品後得到金錢
    REDEEM = 'REDEEM'
