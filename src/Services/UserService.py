from Repositories.UserRepository import UserRepository 
class UserService:
    def __init__(self):
        self.UserRepository = UserRepository();

    def firstOrCreate(self, user, isUnDeleted: bool = False):
        User = self.UserRepository.findByUUID(uuid=user.id, name=user.display_name)
        User = User or self.UserRepository.create(uuid=user.id, name=user.display_name, balance=500) # 預設新手獎金 500 元

        # 如果有給予 isUnDeleted 參數，且 User 不為 None，則進行還原刪除操作
        if User is not None and isUnDeleted:
            self.UserRepository.undelete(User['id'])

        return User

    def getRichestUsers(self, limit: int = 1):
        return self.UserRepository.getRichestUsers(limit=limit)

    def getCheckInChampions(self, limit: int = 1):
        return self.UserRepository.getCheckInChampions(limit=limit)

    def findById(self, id):
        return self.UserRepository.findById(id);

    def getInactivePaginates(self, days=30, page: int = 1, page_size: int = 10):
        return self.UserRepository.getInactivePaginates(days=int(days), page=page, page_size=page_size);

    def getAllMemberPaginates(self, page: int = 1, page_size: int = 10):
        return self.UserRepository.getAllMemberPaginates(page=page, page_size=page_size);

    @staticmethod
    def resetDailyCheckIn():
        return UserRepository.resetDailyCheckIn();

    @staticmethod
    async def sendMessage(bot, guildId, uuid, message: str):
        guild = bot.get_guild(guildId) # 取得伺服器物件
        user  = guild.get_member(uuid) or await bot.fetch_user(uuid) # 從伺服器快取取得使用者物件, 若找不到則從 API 取得
        async def send_message(user, message): # 宣告一個 function 來發送訊息
            await user.send(message)
        bot.loop.create_task(send_message(user, message)) # 使用 create_task 來非同步發送訊息 

    def undelete(self, uuid):
        """
        undelete 還原使用者資料 (SOFT UNDELETE)

        :param uuid: 使用者的 UUID
        :return: None
        """
        return self.UserRepository.undelete(uuid)

    def delete(self, uuid):
        """
        delete 刪除使用者資料 (SOFT DELETE)

        :param uuid: 使用者的 UUID
        :return: None
        """
        return self.UserRepository.delete(uuid)
    
    def updateLastMessageAt(self, user: dict):
        """
        updateLastMessageAt 更新使用者的最後訊息時間

        :param user: 使用者物件
        :param lastMessageAt: 最後訊息時間
        :return: None
        """
        return self.UserRepository.updateLastMessageAt(user)