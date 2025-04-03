from Repositories.UserRepository import UserRepository 
class UserService:
    def __init__(self):
        self.UserRepository = UserRepository();

    def firstOrCreate(self, user):
        User = self.UserRepository.findByUUID(uuid=user.id, name=user.display_name);
        
        if User is None:
            User = self.UserRepository.create(uuid=user.id, name=user.display_name);
        
        return User;

    def findById(self, id):
        return self.UserRepository.findById(id);