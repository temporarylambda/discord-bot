from Repositories.UserRepository import UserRepository 
class UserService:
    def __init__(self):
        self.UserRepository = UserRepository();

    def firstOrCreate(self, user):
        User = self.UserRepository.findByUUID(uuid=user.id, name=user.display_name)
        User = User or self.UserRepository.create(uuid=user.id, name=user.display_name, balance=500) # 預設新手獎金 500 元
        return User

    def getRichestUsers(self, limit: int = 1):
        return self.UserRepository.getRichestUsers(limit=limit)

    def getCheckInChampions(self, limit: int = 1):
        return self.UserRepository.getCheckInChampions(limit=limit)

    def findById(self, id):
        return self.UserRepository.findById(id);

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