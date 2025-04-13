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

def exceptionHandler(func):
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        try:
            await func(self, interaction, *args, **kwargs)
        except GamblingException as e:
            print(e)
            await interaction.response.send_message(e.message, ephemeral=True)
    return wrapper

class GamblingDicesEighteenView(discord.ui.View):
    def __init__(self, amount: int):
        super().__init__(timeout=None)
        self.Gambling = None
        self.amount = amount
        
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

        # 發送訊息
        file = discord.File("resources/images/gambling/welcome-gambling.png", filename="welcome-gambling.png")
        embed = discord.Embed(title="賭局開啟", description=f"{interaction.user.mention} 開啟了一場賭局！")
        embed.add_field(name="賭局類型", value="十八仔", inline=True)
        embed.add_field(name="賭金門檻", value=f"{self.amount} 元", inline=True)
        embed.set_image(url="attachment://welcome-gambling.png")

        embed.description  = "\n\n"
        embed.description += "目前參加者：\n"
        embed.description += f"- {interaction.user.mention} (主持人)"

        await interaction.response.send_message(embed=embed, file=file, view=self)

    @discord.ui.button(label="加入賭局", style=discord.ButtonStyle.primary)
    @exceptionHandler
    async def joinGame(self, interaction: discord.Interaction, button: discord.ui.Button):
        User = self.UserService.firstOrCreate(interaction.user)
        if (str(self.Gambling['user_id']) == str(User['id'])):
            raise GamblingException("您目前無法使用功能，由於：\n**您無法加入您自己的賭局。**")

        embed = interaction.message.embeds[0]
        embed.description += f"\n- {interaction.user.mention}"
        self.GamblingService.join(User, self.Gambling)

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="關閉／退出賭局", style=discord.ButtonStyle.danger, custom_id="btn_closeGame")
    @exceptionHandler
    async def closeGame(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

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
        btn = self.get_item(button_id)
        if btn:
            if toggle:  # 隱藏按鈕
                self.remove_item(btn)
            else:  # 顯示按鈕
                self.add_item(btn)
            await self.message.edit(view=self)  # 更新視圖以反映按鈕狀態
        return
    
    def get_button(self, button_id):
        btn = next((item for item in self.children if isinstance(item, discord.ui.Button) and item.custom_id == button_id), None)
        return btn

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

        await (GamblingDicesEighteenView(amount=amount)).start(interaction)

 

async def setup(bot):
    await bot.add_cog(GamblingDicesEighteen(bot))
    pass
