from Repositories.UserRepository import UserRepository 
from Repositories.UserInventoryRepository import UserInventoryRepository
class UserInventoryService:
    def __init__(self):
        self.UserRepository = UserRepository()
        self.UserInventoryRepository = UserInventoryRepository()

    def firstOrCreate(self, user):
        User = self.UserRepository.findByUUID(uuid=user.id, name=user.display_name)
        
        if User is None:
            User = self.UserRepository.create(uuid=user.id, name=user.display_name)
        
        return User;

    def findById(self, id):
        return self.UserRepository.findById(id)

    def getAll(self, user_id, page: int = 1, page_size: int = 10):
        return self.UserInventoryRepository.getAll(user_id, page=page, page_size=page_size)
