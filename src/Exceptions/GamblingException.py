from discord import app_commands
class GamblingException(app_commands.CheckFailure):
    """
    自定義的賭局異常類別，繼承自 app_commands.CheckFailure
    用於處理賭局相關的異常情況
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    @staticmethod
    def NOT_HOSTED():
        """
        當前用戶並未主持任何賭局

        :return: GamblingException
        """
        return GamblingException("您目前無法使用功能，由於：\n**您並未主持任何一場賭局。**")
    
    @staticmethod
    def NOT_THIS_HOSTED():
        """
        當前用戶並未主持該賭局

        :return: GamblingException
        """
        return GamblingException("您目前無法使用功能，由於：\n**您並非這場賭局的主持人。**")
    
    @staticmethod
    def NOT_ENOUGH_MONEY(money: int = None, currentBalance: int = None):
        """
        當前用戶的金錢不足

        :param money: 需要的金錢
        :return: GamblingException
        """
        message  = "您目前無法使用功能，由於：\n"
        message += "**您的金錢不足支付賭金。**"
        if (money is not None):
            message += f"\n**至少需要 {money} 元。**"

        if (currentBalance is not None):
            message += f"\n**您目前餘額為 {currentBalance} 元。**"
        
        return GamblingException(message)
    
    @staticmethod
    def NOT_BETTED():
        """
        當前用戶並未下注

        :return: GamblingException
        """
        return GamblingException("您目前無法使用功能，由於：\n**您並未下注。**")
    
    @staticmethod
    def STATUS_PENDING():
        """
        當前用戶的賭局尚未開始

        :return: GamblingException
        """
        return GamblingException("您目前無法使用功能，由於：\n**您的賭局尚未開始。**")
    
    @staticmethod
    def STATUS_GAMBLING():
        """
        當前用戶的賭局正在進行中，尚未結束

        :return: GamblingException
        """
        return GamblingException("您目前無法使用功能，由於：\n**您的賭局正在進行中，尚未結束。**")

    @staticmethod
    def STATUS_CANCELED():
        """
        當前用戶的賭局已經遭取消

        :return: GamblingException
        """
        return GamblingException("您目前無法使用功能，由於：\n**您的賭局已經遭取消。**")
    
    @staticmethod
    def STATUS_FINISHED():
        """
        當前用戶的賭局已經結束

        :return: GamblingException
        """
        return GamblingException("您目前無法使用功能，由於：\n**您的賭局已經結束。**")