import os
import discord
from discord.ext import commands
from discord import app_commands
from zoneinfo import ZoneInfo
from Exceptions.RoleException import RoleException
from Services.UserService import UserService
import asyncio

# 宣告機器人
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(error)
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message(error.message, ephemeral=True)

# 宣告連線就緒事件
@bot.event
async def on_ready():
    timezone = ZoneInfo("Asia/Taipei")
    print('============================================================')
    print(f"\n💯 登入成功，機器人身份為： {bot.user.name} - {bot.user.id}")
    print(f" |- 💻 伺服器數量： {len(bot.guilds)}")
    for guild in bot.guilds:
        print(f"    |- 🌐 伺服器名稱： {guild.name} - {guild.id}")
        print(f"        |-- 👥 會員數量： {guild.member_count}")
    print(f" |- 📅 當前時間： {discord.utils.utcnow().astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" |- 👾 版本號： {discord.__version__}")
    print(f" |---------------------- 開始載入 Cog -----------------------")
    synced_commands = await bot.tree.sync()
    print(f" |----------- ✅ 同步指令成功！共 同步了 {len(synced_commands)} 個指令 -----------")  
    if len(synced_commands) > 0:
        print(f" |- 📜 指令列表：")
        for command in synced_commands:
            print(f" |---- {command.name}")
    else:
        print(f" |- 📜 指令列表： 無")
    print(f" |----------------------------------------------------------")
    print(f"\n  若你尚未邀請你的機器人，請點擊以下連結：")
    print(f"  https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8")
    print(f"\n")
    print('=========================初始化完成=========================')

@bot.event
async def on_member_join(member: discord.Member):
    print(f"{member} 加入了伺服器 {member.guild.name}")
    UserServiceObject = UserService()
    UserServiceObject.firstOrCreate(member) # 建立資料庫紀錄

@bot.event
async def on_member_remove(member: discord.Member):
    print(f"{member} 離開了伺服器 {member.guild.name}")
    UserServiceObject = UserService()
    UserServiceObject.delete(member.id) # 刪除資料庫紀錄

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.guild is None:
        return

    UserServiceObject = UserService()
    User = UserServiceObject.firstOrCreate(message.author) # 建立資料庫紀錄

    if User is not None:
        UserServiceObject.updateLastMessageAt(User)


async def load_cogs():
    # 載入所有的 cogs
    for filename in os.listdir("./Cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"Cogs.{filename[:-3]}")
            print(f"載入 {filename} 成功！")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

asyncio.run(main())
