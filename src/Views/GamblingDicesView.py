import discord
import random
from typing import Callable
from Services.UserService import UserService
from Services.GamblingService import GamblingService
from Services.GamblerService import GamblerService
from Services.TransferService import TransferService
from Enums.GamblingType import GamblingType
from Enums.TransferReasonType import TransferReasonType

class GamblingDicesView(discord.ui.View):
    def __init__(self, bot, Host: dict, amount: int, diceEmojis: dict = None) -> None:
        super().__init__(timeout=None)
        self.UserService = UserService();
        self.GamblingService = GamblingService()
        self.GamblerService = GamblerService()
        self.TransferService = TransferService()

        # 機器人
        self.bot                = bot

        # 主持人 (users.*)
        self.Host               = Host

        # 賭局賭金
        self.amount             = amount

        # 骰字 Emoji
        self.diceEmojis         = diceEmojis

        # 是否有骰子 emoji
        self.isHaveDiceEmoji    = (len(diceEmojis.items()) == 6)
        
        # 玩家資料
        self.players            = {
            Host['id']: Host
        }

        # 擲骰子結果
        self.dices              = {}

        # 賭局資料
        self.Gambling           = None

        # embed 物件
        self.embed              = None

        # 更新第一次的 embed
        self.updateEmbed()

    # 更新賭局資訊
    def updateEmbed(self: discord.ui.View) -> None:
        """
        更新賭局的說明文字
        """
        self.embed = discord.Embed(title="十八仔 - 賭局開始！", description="", color=discord.Colour.blue())
        self.embed.description = "操作方式：\n"
        self.embed.description += "1. 點擊「加入賭局」按鈕來參加賭局，賭金將提前從戶頭中扣除。\n"
        self.embed.description += "2. 當主持人確定要開始遊戲時，可以按下「開始遊戲」來開始遊戲。\n"
        self.embed.description += "3. 開始遊戲後，參與者可以點擊「擲骰」按鈕來擲骰。\n"
        self.embed.description += "4. 當所有參與者都擲完骰子後，將會自動進行結算。\n"
        self.embed.description += "5. 當遊戲結算後，整個賭局的累計賭金將會發送給贏家。\n"
        self.embed.description += "6. 若有任何問題，請聯繫主持人或管理員。\n"
        
        self.embed.add_field(name="主持人：", value=f"<@{self.Host['uuid']}>", inline=True)
        self.embed.add_field(name="參加賭金：", value=f"{self.amount} 元", inline=True)
        self.embed.add_field(name="賭局類型：", value="十八仔", inline=True)

        try:
            gamblers = []
            for _, user in self.players.items():
                description  = f"- <@{user['uuid']}>"
                if user['id'] in self.dices:
                    diceEmojis = self.getDicesDisplay(self.dices[int(user['id'])])
                    description += f" - 已擲骰： {diceEmojis}，總和為 {sum(self.dices[int(user['id'])])} 點！"
                gamblers.append(description)

            self.embed.add_field(name="目前參與者：", value="\n".join(gamblers), inline=False)
        except Exception as e:
            print(f"Error: {e}")

    # 發送邀請
    async def sendInvite(self: discord.ui.View, interaction: discord.Interaction) -> None:
        """
        發送賭局邀請訊息
        
        :param interaction: Discord 互動對象
        :type interaction: discord.Interaction
        :return: None
        """
        if self.amount < 0:
            await interaction.response.send_message("請輸入正確的賭注金額！", ephemeral=True)
            return
        elif int(self.Host['balance']) < self.amount:
            await interaction.response.send_message(f"{interaction.user.mention} 抱歉！您的餘額不足，無法開啟賭局！", ephemeral=True)
            return

        try:
            # 建立賭局
            self.Gambling = self.GamblingService.create(User=self.Host, min_bet=self.amount, max_bet=self.amount, type=GamblingType.DICES_EIGHTEEN)

            # 主持人加入賭局
            self.GamblerService.join(Gambling=self.Gambling, User=self.Host)

            # 設定主持人的賭金
            self.GamblerService.raiseBet(Gambling=self.Gambling, User=self.Host, bet=self.amount)

            # 轉帳從主持人的帳戶扣錢至系統帳號
            self.TransferService.transfer(
                FromUser=self.Host, 
                ToUser=None, 
                amount=self.amount, 
                fee=0, 
                reason=f"開啟賭局 - {self.Gambling['id']}", 
                transfer_type=TransferReasonType.BET,
                relation_dict=[
                    {
                        'type': 'GAMBLING',
                        'id': self.Gambling['id']
                    }
                ]
            )
        except Exception as e:
            print(f"Error: {e}")
            await interaction.response.send_message(f"發生錯誤：{e}", ephemeral=True)
            return

        await interaction.response.send_message(f"{interaction.user.mention} 開啟了一場賭局！", view=self, embed=self.embed)

    # 加入賭局按鈕
    @discord.ui.button(label="加入賭局", style=discord.ButtonStyle.primary, custom_id="join_game")
    async def join_game(self: discord.ui.View, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        參加賭局的按鈕回調函數

        :param interaction: Discord 互動對象
        :type interaction: discord.Interaction
        :param button: Discord 按鈕對象
        :type button: discord.ui.Button
        :return: None
        """
        User = self.UserService.firstOrCreate(interaction.user)
        if User['id'] == self.Host['id']:
            await interaction.response.send_message("你無法加入自己的賭局！", ephemeral=True)
            return
        elif User['id'] in self.players:
            await interaction.response.send_message("你已經加入過了！", ephemeral=True)
            return
        elif int(User['balance']) < self.amount:
            await interaction.response.send_message(f"{interaction.user.mention} 抱歉！您的餘額不足，無法加入賭局！", ephemeral=True)
            return

        self.players[User['id']] = User
        self.updateEmbed()

        message = interaction.message
        await interaction.response.send_message(f"{interaction.user.mention} 您成功加入賭局！\n已從您的帳戶中預先扣除 {self.amount} 元", ephemeral=True)
        await message.edit(embed=self.embed, view=self)

    # 開始遊戲按鈕
    @discord.ui.button(label="開始遊戲", style=discord.ButtonStyle.success, custom_id="start_game")
    async def start_game(self: discord.ui.View, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        開始遊戲的按鈕回調函數

        :param interaction: Discord 互動對象
        :type interaction: discord.Interaction
        :param button: Discord 按鈕對象
        :type button: discord.ui.Button
        :return: None
        """
        User = self.UserService.firstOrCreate(interaction.user)
        if User['id'] != self.Host['id']:
            await interaction.response.send_message("只有主持人可以開始賭局。", ephemeral=True)
            return

        try:
            # 移除加入與開始按鈕
            self.clear_items()

            # 新增擲骰按鈕與結算按鈕
            Button = discord.ui.Button(label="擲骰", style=discord.ButtonStyle.primary, custom_id="roll_dices");
            Button.callback = self.roll_dices
            self.add_item(Button)

            # self.add_item(self.RollDiceButton(view=self)) # TODO
            # self.add_item(self.SettleButton(view=self)) # TODO

            await interaction.response.edit_message(content="賭局開始！請各位參與者依序擲骰！", view=self)
        except Exception as e:
            print(f"Error: {e}")
            await interaction.response.send_message(f"發生錯誤：{e}", ephemeral=True)
            return

    # 投擲骰子按鈕
    async def roll_dices(self: discord.ui.View, interaction: discord.Interaction) -> None:
        """
        擲骰子

        :param interaction: Discord 互動對象
        :type interaction: discord.Interaction
        :param player: 玩家資訊
        :type player: dict
        :return: None
        """
        User = self.UserService.firstOrCreate(interaction.user)
        if User['id'] not in self.players:
            await interaction.response.send_message("你並非這場賭局的成員！", ephemeral=True)
            return
        elif User['id'] in self.dices:
            await interaction.response.send_message("你已經擲過骰子了！", ephemeral=True)
            return

        dices = (random.randint(1, 6), random.randint(1, 6), random.randint(1, 6),)
        self.dices[User['id']] = dices

        # 當有設定 emoji 時轉使用 emoji
        diceEmojis = self.getDicesDisplay(dices)

        self.updateEmbed()
        await interaction.message.edit(embed=self.embed, view=self)
        await interaction.response.send_message(f"{interaction.user.mention} 擲出了骰子： {diceEmojis}，總和為 {sum(dices)} 點！")

        try:
            if (len(self.dices) == len(self.players)):
                await self.settle_game(interaction)
        except Exception as e:
            print(f"Error: {e}")
            return

    # 結算遊戲按鈕
    async def settle_game(self: discord.ui.View, interaction: discord.Interaction) -> None:
        """
        結算遊戲

        :param interaction: Discord 互動對象
        :type interaction: discord.Interaction
        :return: None
        """

        maxDicer = None
        for playerId, dices in self.dices.items():
            diceSum = sum(dices)
            if maxDicer is None or diceSum > maxDicer[1]:
                maxDicer = (playerId, diceSum)

        diceEmojis = self.getDicesDisplay(self.dices[maxDicer[0]])
        await interaction.message.edit(view=None)
        await interaction.channel.send(content=f"遊戲結束！\n\n贏家是 <@{self.players[maxDicer[0]]['uuid']}>！\n擲出的骰子為 {diceEmojis}，總和為 {maxDicer[1]}！")

    # 取得骰子輸出結果
    def getDicesDisplay(self: discord.ui.View, dices: list) -> list:
        """
        取得骰子顯示字串

        :param dices: 骰子列表
        :type dices: list
        :return: list
        """

        diceEmojis = [str(dice) for dice in dices]
        if self.isHaveDiceEmoji:
            diceEmojis = [self.diceEmojis[dice] for dice in dices]
        diceEmojis = ' '.join(map(str, diceEmojis))
        return diceEmojis

