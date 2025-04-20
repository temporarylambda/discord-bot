import discord
import os
from discord import app_commands
from Exceptions.RoleException import RoleException

class RoleService:
    @staticmethod
    async def hasRole(Guild: discord.Guild, DiscordUser: discord.User, RoleEnvKey: str, default=False):
        """
        檢查是否擁有特定身份組

        :param Guild: 目標伺服器
        :param DiscordUser: 目標使用者
        :param RoleEnvKey: 環境變數的鍵值
        :param default: 預設值 - 如果查無資料應該當作擁有(True)還是沒有(False)
        :return: 是否擁有該身份組
        """
        member = Guild.get_member(DiscordUser.id)
        if member is None:
            try:
                member = await Guild.fetch_member(DiscordUser.id)
            except discord.NotFound:
                return default
        
        RoleIds = [id.strip() for id in os.getenv(RoleEnvKey, "").split(",") if id.strip()]
        return any(str(role.id) in RoleIds for role in member.roles)

    @staticmethod
    def checkBanned(boolean: bool = False):
        """
        檢查是否擁有懲罰性身份組

        :param boolean: True 代表允許懲罰性身份組，False 代表禁止懲罰性身份組
        :raise RoleException: 如果不符合條件則拋出異常
        """
        async def predicate(interaction: discord.Interaction):
            isHaveRole = await RoleService.hasRole(interaction.guild, interaction.user, "ROLE_BANNED", default=True)
            if (boolean ^ isHaveRole):
                raise RoleException("你目前被給予了懲罰性身份組，暫時無法使用此指令，\n若有疑問請透過客服單向管理員反應。")
            return True
        return app_commands.check(predicate)

    @staticmethod
    def checkManager(boolean: bool = True):
        """
        檢查是否擁有管理員身份組

        :param boolean: True 代表允許管理員身份組，False 代表禁止管理員身份組
        :raise RoleException: 如果不符合條件則拋出異常
        """
        async def predicate(interaction: discord.Interaction):
            isHaveRole = await RoleService.hasRole(interaction.guild, interaction.user, "ROLE_MANAGER", default=False)
            if (boolean ^ isHaveRole):
                raise RoleException("此指令僅限管理員使用\n若有疑問請透過客服單向管理員反應。")
            return True
        return app_commands.check(predicate)