# from typing import Literal, Union, NamedTuple
# from enum import Enum
from Services.UserService import UserService
import os
import discord
from discord import app_commands

MY_GUILD = discord.Object(id=os.getenv("DISCORD_GUILD_ID"))  # 替換為你的伺服器 ID
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

client = MyClient()

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.tree.command(name='個人資料', description='查詢個人資料')
async def personal_data(interaction: discord.Interaction,):
    UserServiceObject = UserService();
    User = UserServiceObject.firstOrCreate(user=interaction.user);

    embed = discord.Embed(title="個人資料查詢", description=f"{interaction.user.mention} 您好！\n這是您的個人資料！")
    embed.add_field(name="錢包餘額", value=f"{User['balance']} 元", inline=False)
    embed.add_field(name="連續簽到連勝", value=f"{User['consecutive_checkin_days']} 日", inline=False)
    await interaction.response.send_message(embed=embed)

    await interaction.response.send_message(embed=embed)

client.run(os.getenv("DISCORD_BOT_TOKEN"))
