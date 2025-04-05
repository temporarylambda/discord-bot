import os
import discord
from discord.ext import commands
from discord import app_commands, Colour
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
    @app_commands.describe(user="要給予的用戶", amount="金錢數量", note="給予的理由或備註 - 若沒有則不填")
    @RoleService.checkIsNotBanned()
    @RoleService.checkIsManager()
    async def giveMoney(self, interaction: discord.Interaction, user: discord.Member, amount: int, note: str = None):
        UserServiceObject = UserService()
        AdminUser   = UserServiceObject.firstOrCreate(interaction.user)
        ToUser      = UserServiceObject.firstOrCreate(user)

        TransferServiceObject = TransferService()
        TransferServiceObject.giveMoney(AdminUser, ToUser, amount, note)

        embed = discord.Embed(title="管理方操作", description="", color=Colour.gold())
        embed.add_field(name="發放對象", value=ToUser['name'], inline=False)
        embed.add_field(name="發放金額", value=f"{amount} 元", inline=False)
        if note is not None:
            embed.add_field(name="備註", value=note, inline=False)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_footer(text=f"由 {interaction.user.display_name} 操作")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="金錢扣除", description="扣除用戶帳上金錢 - 若用戶沒有足夠金錢，則會扣除至負數")
    @app_commands.describe(user="要扣除的用戶", amount="金錢數量", note="扣除的理由或備註 - 若沒有則不填")
    @RoleService.checkIsNotBanned()
    @RoleService.checkIsManager()
    async def takeMoney(self, interaction: discord.Interaction, user: discord.Member, amount: int, note: str = None):
        UserServiceObject = UserService()
        AdminUser   = UserServiceObject.firstOrCreate(interaction.user)
        ToUser      = UserServiceObject.firstOrCreate(user)

        TransferServiceObject = TransferService()
        TransferServiceObject.takeMoney(AdminUser, ToUser, amount, note)

        embed = discord.Embed(title="管理方操作", description="", color=Colour.gold())
        embed.add_field(name="扣除對象", value=ToUser['name'], inline=False)
        embed.add_field(name="扣除金額", value=f"{amount} 元", inline=False)
        if note is not None:
            embed.add_field(name="備註", value=note, inline=False)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_footer(text=f"由 {interaction.user.display_name} 操作")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Manager(bot))
