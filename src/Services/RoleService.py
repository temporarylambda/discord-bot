import discord
import os
from discord import app_commands
from Exceptions.RoleException import RoleException

class RoleService:
    @staticmethod
    async def hasRole(Guild: discord.Guild, DiscordUser: discord.User, RoleEnvKey: str, default=False):
        member = Guild.get_member(DiscordUser.id)
        if member is None:
            try:
                member = await Guild.fetch_member(DiscordUser.id)
            except discord.NotFound:
                return default
        
        RoleIds = [id.strip() for id in os.getenv(RoleEnvKey, "").split(",") if id.strip()]
        return any(str(role.id) in RoleIds for role in member.roles)

    @staticmethod
    def checkIsNotBanned():
        async def predicate(interaction: discord.Interaction):
            if await RoleService.hasRole(interaction.guild, interaction.user, "ROLE_BANNED", default=True):
                raise RoleException("你目前被給予了懲罰性身份組，暫時無法使用此指令，\n若有疑問請透過客服單向管理員反應。")
            return True
        return app_commands.check(predicate)

    @staticmethod
    def checkIsManager():
        async def predicate(interaction: discord.Interaction):
            if not (await RoleService.hasRole(interaction.guild, interaction.user, "ROLE_MANAGER", default=False)):
                raise RoleException("此指令僅限管理員使用\n若有疑問請透過客服單向管理員反應。")
            return True
        return app_commands.check(predicate)