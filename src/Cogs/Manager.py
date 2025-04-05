import os
import discord
from discord.ext import commands
from discord import app_commands
from Services.RoleService import RoleService
from Services.UserService import UserService
from Services.TransferService import TransferService

class Manager(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    @app_commands.command(name="金錢發放", description="給予用戶金錢")
    @app_commands.describe(User="要給予的用戶", amount="金錢數量")
    @RoleService.checkIsNotBanned()
    @RoleService.checkIsManager()
    async def giveMoney(self, interaction: discord.Interaction, User: discord.Member, amount: int):
        # print(interaction, User)
        # UserServiceObject = UserService()
        # AdminUser   = UserServiceObject.firstOrCreate(interaction.user.id, interaction.user.name)
        # User        = UserServiceObject.firstOrCreate(User.id, User.name)

        # print(AdminUser, User)
        # TransferServiceObject = TransferService()
        # TransferServiceObject.giveMoney(AdminUser, User, amount)

        # embed = discord.Embed(title="管理方操作", description=f"給予 {User.display_name} {amount} 金幣", color='#F1C40F')
        # embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        # embed.set_footer(text=f"由 {interaction.user.name} 操作")
        # embed.timestamp = discord.utils.utcnow()
        # await interaction.response.send_message(embed=embed)

        await interaction.response.send_message(f"{interaction.user.mention} 給予 {User.display_name} {amount} 金幣")

    @app_commands.command(name="金錢扣除", description="扣除用戶帳上金錢 - 若用戶沒有足夠金錢，則會扣除至負數")
    @app_commands.describe(User="要扣除的用戶", amount="金錢數量")
    @RoleService.checkIsNotBanned()
    @RoleService.checkIsManager()
    async def takeMoney(self, interaction: discord.Interaction, User: discord.Member, amount: int):
        await interaction.response.send_message(f"扣除 {User.display_name} {amount} 金幣")

async def setup(bot):
    await bot.add_cog(Manager(bot))
