import discord
from discord.ext import commands
from discord import app_commands

from Services.UserService import UserService

class Personal(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    @app_commands.command(name="個人資料", description="查詢個人資料")
    async def personal_data(self, interaction: discord.Interaction):
        UserServiceObject = UserService();
        User = UserServiceObject.firstOrCreate(user=interaction.user);

        embed = discord.Embed(title="個人資料查詢", description=f"{interaction.user.mention} 您好！\n這是您的個人資料！")
        embed.add_field(name="錢包餘額", value=f"{User['balance']} 元", inline=False)
        embed.add_field(name="連續簽到連勝", value=f"{User['consecutive_checkin_days']} 日", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="富翁榜", description="列出伺服器內前十名大富翁！")
    async def richest(self, interaction: discord.Interaction):
        UserServiceObject = UserService()
        RichestUsers = UserServiceObject.getRichestUsers(10)

        embed = discord.Embed(title="富翁榜", description=f"{interaction.user.mention} 您好！\n這是伺服器內前十名大富翁！")
        for index, user in enumerate(RichestUsers):
            embed.add_field(name=f"**{index + 1}.** {user['name']}", value=f"{user['balance']} 元", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="簽到榜", description="列出伺服器內前十名簽到王！")
    async def richest(self, interaction: discord.Interaction):
        UserServiceObject = UserService()
        RichestUsers = UserServiceObject.getRichestUsers(10)

        embed = discord.Embed(title="簽到榜", description=f"{interaction.user.mention} 您好！\n這是伺服器內前十名簽到王！")
        for index, user in enumerate(RichestUsers):
            embed.add_field(name=f"**{index + 1}.** {user['name']}", value=f"{user['consecutive_checkin_days']} 連勝", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Personal(bot))
