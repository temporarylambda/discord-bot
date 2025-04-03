from Repositories.MerchandiseRepository import MerchandiseRepository 
class MerchandiseService:
    def __init__(self):
        self.MerchandiseRepository = MerchandiseRepository();

    def findById(self, id):
        return self.MerchandiseRepository.findById(id);

    def getAll(self, user_id, page: int = 1, page_size: int = 10):
        return self.MerchandiseRepository.getAll(user_id, page, page_size);