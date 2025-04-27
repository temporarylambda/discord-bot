import discord
from discord.ext import commands
from discord import app_commands
from Services.RoleService import RoleService
from Services.UserService import UserService
from Views.GamblingDicesView import GamblingDicesView

class GamblingDiceEighteen(commands.GroupCog, name="十八仔"):
    def __init__(self, bot):
        self.bot = bot
        self.UserService = UserService()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    @app_commands.command(name='開始賭局', description=f'開啟一場十八仔賭局')
    @app_commands.describe(amount='賭注金額', rule='賭局模式')
    @app_commands.choices(rule=[
        app_commands.Choice(name="點數最大者贏", value="DESC"),
        app_commands.Choice(name="點數最小者贏", value="ASC"),
    ])
    @RoleService.checkBanned(False)
    async def startGame(self, interaction: discord.Interaction, amount: int, rule: str = "DESC"):
        diceEmojis = {}
        for i in range(1, 7):
            diceEmojis[i] = discord.utils.get(interaction.guild.emojis, name=f"emoji_dice_{i}")

        User = self.UserService.firstOrCreate(interaction.user)
        View = GamblingDicesView(self.bot, Host=User, amount=amount, diceEmojis=diceEmojis, sort_order=rule)
        await View.sendInvite(interaction)

async def setup(bot):
    await bot.add_cog(GamblingDiceEighteen(bot))
