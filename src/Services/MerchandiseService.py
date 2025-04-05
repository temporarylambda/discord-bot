from Repositories.MerchandiseRepository import MerchandiseRepository 
class MerchandiseService:
    def __init__(self):
        self.MerchandiseRepository = MerchandiseRepository();

    def findById(self, id):
        return self.MerchandiseRepository.findById(id);

    def getAll(self, user_id = None):
        return self.MerchandiseRepository.getAll(user_id);

    def getAllPaginates(self, user_id, page: int = 1, page_size: int = 10):
        return self.MerchandiseRepository.getAllPaginates(user_id, page, page_size);

    def create(self, user_id, merchandise):
        print(user_id, merchandise)
        return self.MerchandiseRepository.create(user_id, merchandise);

    def delete(self, ids):
        return self.MerchandiseRepository.delete(ids);