import os
import discord
from discord.ext import commands
from discord import app_commands
from Services.UserService import UserService
from Services.TransferService import TransferService
from Services.RoleService import RoleService

class GamblingDicesEighteen(commands.GroupCog, name="十八仔"):
    def __init__(self, bot):
        self.bot = bot
    
    @staticmethod
    def checkHosted(boolean: bool = True):
        async def predicate(interaction: discord.Interaction):
            # TODO: 檢查是否是賭局主持人
            # if await SomethingReturn() == boolean:
            #     raise GamblingDicesEighteenException("你是賭局主持人，無法執行此指令")
            # else:
            #     raise GamblingDicesEighteenException("你不是賭局主持人，無法執行此指令")
            return True
        return app_commands.check(predicate)
    
    @staticmethod
    def checkJoined(boolean: bool = True):
        async def predicate(interaction: discord.Interaction):
            # TODO: 檢查是否是賭局參加者 - 賭局主持人也算是賭局參加者
            # if await SomethingReturn() == boolean:
            #     raise GamblingDicesEighteenException("你是賭局參加者，無法執行此指令")
            # else:
            #     raise GamblingDicesEighteenException("你不是賭局參加者，無法執行此指令")
            return True
        return app_commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    # TODO: 開啟賭局
    @app_commands.command(name='開啟賭局')
    @app_commands.describe(amount="加入賭局的賭金，可為 0 元")
    @commands.check(checkHosted(True))
    # 必須不是賭局開啟者、不是賭局參加者才能使用此指令 - 有必要嗎？是不是可以實現同時參與多場賭局？
    @RoleService.checkIsNotBanned()
    async def startGame(self, interaction: discord.Interaction, amount: int):
        pass

    # TODO: 加入賭局
    @app_commands.command(name='加入賭局')
    @app_commands.describe(amount="加入賭局的賭金")
    # 必須不是賭局開啟者、不是賭局參加者才能使用此指令 - 有必要嗎？是不是可以實現同時參與多場賭局？
    @RoleService.checkIsNotBanned()
    async def joinGame(self, interaction: discord.Interaction, amount: int):
        pass

    # TODO: 擲骰
    @app_commands.command(name='擲骰')
    # 必須是賭局主持人或是賭局參加者才能使用此指令
    @RoleService.checkIsNotBanned()
    async def roleDices(self, interaction: discord.Interaction):
        pass
    
    # TODO: 檢查賭局勝出者
    async def checkWinner():
        pass

    # TODO: 處理賭金發放
    async def dealWithBets():
        pass
 

async def setup(bot):
    await bot.add_cog(GamblingDicesEighteen(bot))
