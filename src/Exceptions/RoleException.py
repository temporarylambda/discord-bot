from discord import app_commands
class RoleException(app_commands.CheckFailure):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message