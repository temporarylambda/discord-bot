from Repositories.UserRepository import UserRepository 
from Repositories.UserInventoryRepository import UserInventoryRepository
class UserInventoryService:
    def __init__(self):
        self.UserRepository = UserRepository()
        self.UserInventoryRepository = UserInventoryRepository()

    def firstByMerchandiseId(self, user_id, merchandise_id):
        return self.UserInventoryRepository.firstByMerchandiseId(user_id, merchandise_id)

    def getAll(self, user_id, page: int = 1, page_size: int = 10):
        return self.UserInventoryRepository.getAll(user_id, page=page, page_size=page_size)

    # 兌換商品
    def redeem(self, inventory_id):
        return self.UserInventoryRepository.redeem(inventory_id)
