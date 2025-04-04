from Repositories.UserRepository import UserRepository 
class UserService:
    def __init__(self):
        self.UserRepository = UserRepository();

    def firstOrCreate(self, user):
        User = self.UserRepository.findByUUID(uuid=user.id, name=user.display_name)
        User = User or self.UserRepository.create(uuid=user.id, name=user.display_name)
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