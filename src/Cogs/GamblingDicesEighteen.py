import os
import discord
from discord.ext import commands
from discord import app_commands
from Services.UserService import UserService
from Services.TransferService import TransferService
from Services.RoleService import RoleService
from Services.GamblingService import GamblingService
from Exceptions.GamblingException import GamblingException
from Enums.GamblingType import GamblingType
from Enums.GamblerStatus import GamblerStatus

def exceptionHandler(func):
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        try:
            await func(self, interaction, *args, **kwargs)
        except GamblingException as e:
            print(e)
            await interaction.response.send_message(e.message, ephemeral=True)
    return wrapper

class GamblingDicesEighteenView(discord.ui.View):
    def __init__(self, amount: int, Host: dict = None):
        super().__init__(timeout=None)
        self.Gambling = None
        self.amount = amount
        self.Host = Host
        
        self.GamblingService = GamblingService()
        self.UserService = UserService()

        # self.btnRollDices = discord.ui.Button(label="擲骰子", style=discord.ButtonStyle.success, custom_id="btn_rollDices")
        # self.btnRollDices.callback = self.rollDices

        # self.btnSummary = discord.ui.Button(label="提前結算", style=discord.ButtonStyle.success, custom_id="btn_summary")
        # self.btnSummary.callback = self.summary

    @exceptionHandler
    async def start(self, interaction=discord.Interaction) -> None:
        """
        初始化賭局視圖

        :param interaction: 互動對象
        :return: None
        """
        User = self.UserService.firstOrCreate(interaction.user)
        if (int(User['balance']) < self.amount):
            raise GamblingException.NOT_ENOUGH_MONEY(self.amount, User['balance'])

        self.Gambling = self.GamblingService.host(User, GamblingType.DICES_EIGHTEEN, self.amount)


        file = discord.File("resources/images/gambling/welcome-gambling.png", filename="welcome-gambling.png")
        await interaction.response.send_message(file=file)

        # 發送訊息
        embed = self.generateEmbed(interaction, User)
        await interaction.followup.send(embed=embed, view=self)

    @discord.ui.button(label="加入賭局", style=discord.ButtonStyle.primary, custom_id="btn_joinGame")
    @exceptionHandler
    async def joinGame(self, interaction: discord.Interaction, button: discord.ui.Button):
        User = self.UserService.firstOrCreate(interaction.user)
        if (str(self.Gambling['user_id']) == str(User['id'])):
            raise GamblingException.SELF_HOSTED()

        embed = self.generateEmbed(interaction, User)
        self.GamblingService.join(User, self.Gambling)
        await interaction.message.delete()
        await interaction.channel.send(embed=embed, view=self)

    @discord.ui.button(label="關閉／退出賭局", style=discord.ButtonStyle.danger, custom_id="btn_closeGame")
    @exceptionHandler
    async def closeGame(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 如果是賭局主持人，則給予空陣列，藉此取出所有的參加者；如果不是賭局主持人，則給予自己的 ID，藉此取出自己
        User = self.UserService.firstOrCreate(interaction.user)
        embed = self.generateEmbed(interaction, User, isExiting=True)
        self.GamblingService.exit(User, self.Gambling)

        if (str(self.Gambling['user_id']) == str(User['id'])):
            print('1')
            await self.hideButton("btn_joinGame", False)
            print('2')
            await self.hideButton("btn_closeGame", True)
            print('3')

        await interaction.message.delete()
        await interaction.channel.send(embed=embed, view=self)

    @exceptionHandler
    async def rollDices(self, interaction, dices):
        pass

    @exceptionHandler
    async def summary(self, interaction, dices):
        pass

    async def hideButton(self, button_id, toggle: bool):
        """
        隱藏或顯示按鈕（直接移除或加入按鈕）

        :param button_id: 按鈕 ID
        :param toggle: True 表示隱藏，False 表示顯示
        """
        btn = self.get_button(button_id)
        if btn:
            if toggle:  # 隱藏按鈕
                self.remove_item(btn)
            else:  # 顯示按鈕
                self.add_item(btn)

    def get_button(self, button_id):
        btn = next((item for item in self.children if isinstance(item, discord.ui.Button) and item.custom_id == button_id), None)
        return btn
    
    def generateEmbed(self, interaction: discord.Interaction, User: dict, isExiting: bool = False):
        # 如果 Gambling 是 None 代表重新新建立，就一定是賭局創辦人
        isHost = (str(User['id']) == str(self.Gambling['user_id'])) if self.Gambling is not None else True 
        isHostExit = (isHost and isExiting)

        # 發送訊息
        embed = discord.Embed(title="賭局開啟" if isHostExit is False else "賭局結束", description="")
        embed.add_field(name="賭局類型", value="十八仔", inline=True)
        embed.add_field(name="賭金門檻", value=f"{self.amount} 元", inline=True)

        # Handle 開始與結束賭局
        embed.description  = f"{interaction.user.mention}" if isHost else f"<@{self.Host['uuid']}>"
        embed.description += ' 結束了一場賭局！' if isHostExit else ' 開啟了一場賭局！'
        embed.description += "\n\n"
        embed.description += "目前參加者：\n"

        Gamblers = self.GamblingService.getGambler(self.Gambling['id']);
        isInclude = False
        for Gambler in Gamblers:
            # 如果要離開的時候，當目前的 Gambler 等於自己時，不用顯示（因為要離開了）   
            if (
                isExiting is True and
                isInclude is False and 
                (str(Gambler['user_id']) == str(User['id']))
            ):
                continue

            elif Gambler['status'] == GamblerStatus.ABSTAIN.value:
                continue

            # 追加當前參加者名稱
            embed.description += f"- {interaction.user.mention}" if isHost else f"- <@{Gambler['uuid']}>"
            embed.description += f" (主持人)" if (str(Gambler['user_id']) == str(self.Host['id'])) else ""
            if (Gambler['status'] == GamblerStatus.WINNER.value):
                embed.description += f" - 贏家"
            elif (Gambler['status'] == GamblerStatus.LOSER.value):
                embed.description += f" - 輸家"
            embed.description += "\n"
        return embed

class GamblingDicesEighteen(commands.GroupCog, name="十八仔"):
    def __init__(self, bot):
        self.bot = bot
        self.UserService = UserService()
        self.GamblingService = GamblingService()
        self.TransferService = TransferService()
    
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
    @RoleService.checkBanned(False)
    async def startGame(self, interaction: discord.Interaction, amount: int):
        User = self.UserService.firstOrCreate(interaction.user)
        if (int(User['balance']) < amount):
            raise GamblingException.NOT_ENOUGH_MONEY(amount, User['balance'])

        await (GamblingDicesEighteenView(amount=amount, Host=User)).start(interaction)

 

async def setup(bot):
    await bot.add_cog(GamblingDicesEighteen(bot))
    pass
