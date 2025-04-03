from Services.UserService import UserService
from Services.TopicService import TopicService
from Views.CurrentTopicDropdownView import CurrentTopicDropdownView
from Services.DatabaseConnection import DatabaseConnection
import os
import discord
from discord.ext import commands
from discord import app_commands

MY_GUILD = discord.Object(id=os.getenv("DISCORD_GUILD_ID"))  # 替換為你的伺服器 ID
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    async def loadCogs(self):
        for filename in os.listdir("./Cogs"):
            if filename.endswith(".py"):
                extension_name = f"Cogs.{filename[:-3]}"
                try:
                    await self.bot.reload_extension(extension_name)
                    print(f"Loaded {filename}")
                except commands.ExtensionNotLoaded:
                    await self.bot.load_extension(extension_name)

client = MyClient()

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id}), 本地時間 {DatabaseConnection.getCurrentTimestamp()}')
    await client.loadCogs()
    print('------')

# # 查看目前個人金額與簽到連勝
# @client.tree.command(name='個人資料', description='查詢個人資料')
# async def personal_data(interaction: discord.Interaction,):
#     UserServiceObject = UserService();
#     User = UserServiceObject.firstOrCreate(user=interaction.user);

#     embed = discord.Embed(title="個人資料查詢", description=f"{interaction.user.mention} 您好！\n這是您的個人資料！")
#     embed.add_field(name="錢包餘額", value=f"{User['balance']} 元", inline=False)
#     embed.add_field(name="連續簽到連勝", value=f"{User['consecutive_checkin_days']} 日", inline=False)
#     await interaction.response.send_message(embed=embed)

# 取得新的簽到題目
@client.tree.command(name='簽到', description='隨機出一則真心話或大挑戰！')
async def daily_check_in(interaction: discord.Interaction):
    UserServiceObject = UserService()
    User = UserServiceObject.firstOrCreate(interaction.user)

    TopicServiceObject = TopicService()
    if TopicServiceObject.isUnavailable(User['id']):
        await interaction.response.send_message(f"{interaction.user.mention} 您目前沒有額度可以領取新的簽到題目，請先完成手上的題目再來簽到！")
        return
    elif TopicServiceObject.isTodayTaken(User['id']):
        await interaction.response.send_message(f"{interaction.user.mention} 今天您已經領取完所有可以領取的題目了！")
        return
    
    DailyCheckInTopic = TopicServiceObject.take(User['id'])
    print(DailyCheckInTopic)
    embed = discord.Embed(title="每日簽到！", description=f"{interaction.user.mention} 您好！\n這是您的簽到題目！")
    embed.add_field(name="題目", value=DailyCheckInTopic['description'], inline=False)
    if int(DailyCheckInTopic['reward']) > 0:
        embed.add_field(name="獎勵", value=f"{DailyCheckInTopic['reward']} 元", inline=False)

    if DailyCheckInTopic['note'] is not None:
        embed.add_field(name="備註", value=DailyCheckInTopic['note'], inline=False)

    await interaction.response.send_message(embed=embed)

# 查看目前手上的簽到題目
@client.tree.command(name='任務', description='查詢目前你的簽到任務')
async def tasks(interaction: discord.Interaction):
    UserServiceObject = UserService()
    User = UserServiceObject.firstOrCreate(interaction.user)

    TopicServiceObject = TopicService()
    DailyCheckInTopics = TopicServiceObject.getCurrentTopics(User['id'])
    if len(DailyCheckInTopics) == 0:
        await interaction.response.send_message(f"{interaction.user.mention} 您目前沒有任何簽到任務！")
        return

    embedDescription = f"# 簽到任務查詢\n{interaction.user.mention} 您好！\n這是您的簽到任務！"
    for DailyCheckInTopic in DailyCheckInTopics:
        embedDescription += f"\n\n題目：{DailyCheckInTopic['description']}"
        if DailyCheckInTopic['reward'] and str(DailyCheckInTopic['reward']).isdigit() and int(DailyCheckInTopic['reward']) > 0:
            embedDescription += f"\n獎勵：{DailyCheckInTopic['reward']} 元"
        
        if DailyCheckInTopic['note'] is not None:
            embedDescription += f"\n備註：{DailyCheckInTopic['note']}"

    embed = discord.Embed(title="簽到任務查詢", description=embedDescription)
    await interaction.response.send_message(embedDescription)

# 呈現下拉選單選擇要回報的任務
@client.tree.command(name='任務回報', description='完成你的簽到任務來獲得獎勵！')
async def tasks_report(interaction: discord.Interaction):
    UserServiceObject = UserService()
    User = UserServiceObject.firstOrCreate(interaction.user)

    TopicServiceObject = TopicService()
    DailyCheckInTopics = TopicServiceObject.getCurrentTopics(User['id'])
    if len(DailyCheckInTopics) == 0:
        await interaction.response.send_message(f"{interaction.user.mention} 您目前沒有任何簽到任務！")
        return

    embed = discord.Embed(title="回報任務", description=f"{interaction.user.mention} 您好！\n這是您目前的簽到題目！\n請選擇題目並按下「確認回報」來進行回報！")
    view = CurrentTopicDropdownView(DailyCheckInTopics)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

client.run(os.getenv("DISCORD_BOT_TOKEN"))
