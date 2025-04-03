import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncio

# 宣告機器人
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# 宣告連線就緒事件
@bot.event
async def on_ready():
    print('============================================================')
    print(f"\n💯 登入成功，機器人身份為： {bot.user.name} - {bot.user.id}")
    print(f" |- 💻 伺服器數量： {len(bot.guilds)}")
    for guild in bot.guilds:
        print(f"    |- 🌐 伺服器名稱： {guild.name} - {guild.id}")
        print(f"        |-- 👥 會員數量： {guild.member_count}")
    print(f" |- 📅 當前 UTC 時間： {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" |- 👾 版本號： {discord.__version__}")
    print(f" |---------------------- 開始載入 Cog -----------------------")
    try:
        synced_commands = await bot.tree.sync()
        print(f" |----------- ✅ 同步指令成功！共 同步了 {len(synced_commands)} 個指令 -----------")  
        if len(synced_commands) > 0:
            print(f" |- 📜 指令列表：")
            for command in synced_commands:
                print(f" |---- {command.name}")
        else:
            print(f" |- 📜 指令列表： 無")
    except Exception as e:
        print(f" |- ❌ 同步指令失敗： {e}")
    print(f" |----------------------------------------------------------")
    print(f"\n  若你尚未邀請你的機器人，請點擊以下連結：")
    print(f"  https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8")
    print(f"\n")
    print('============================================================')

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
