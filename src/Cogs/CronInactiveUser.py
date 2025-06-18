import discord
from discord.ext import tasks, commands
from discord import app_commands
from datetime import datetime, time
from zoneinfo import ZoneInfo
from Services.RoleService import RoleService
from Services.UserService import UserService
from Views.PaginationView import PaginationView
import os

class CronInactiveUser(commands.GroupCog, name="不活躍用戶"):
    midnightTime = time(hour=0, minute=0, second=0, tzinfo=ZoneInfo("Asia/Taipei"))
    executeDays = os.getenv("RULE_INACTIVE_CHECKIN_DAYS", 30)

    def __init__(self, bot):
        self.bot = bot
        self.enable = os.getenv("RULE_INACTIVE_CHECK_ENABLE", "False") == "True"
        self.executeDays = os.getenv("RULE_INACTIVE_CHECKIN_DAYS", 30)
        self.warningDays = os.getenv("RULE_INACTIVE_WARNING_DAYS", 23)
        
        # TODO: 啟動每日檢查任務
        # self.resetDailyCheckIn.start()

    def cog_unload(self):
        # self.resetDailyCheckIn.stop()
        pass

    # # 每天 00:00 進行每日檢查
    # @tasks.loop(time=midnightTime)
    # async def resetDailyCheckIn(self):
    #     today = datetime.now(ZoneInfo("Asia/Taipei")).date()
    #     print(f" |---- {today} - 開始檢查不活躍用戶...")

    # 同步目前尚未建立資料庫資料的群組成員
    @app_commands.command(name="同步", description="同步伺服器與資料庫中的成員名單")
    @RoleService.checkBanned(False)
    @RoleService.checkManager(True)
    async def sync(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send("同步開始 - 更新已經加入伺服器但尚未操作過機器人的名單⋯⋯")
        UserServiceObject = UserService()
        UserServiceObject.firstOrCreate(interaction.user)

        guild = interaction.guild
        # 確保已經有完整的 member list（必要時強制抓取）
        if not guild.chunked:
            await guild.chunk()

        # 排除機器人成員
        members = [member for member in guild.members if not member.bot]

        # 為所有成員創建或更新 User
        for member in members:
            UserServiceObject.firstOrCreate(member)
        await interaction.followup.send("更新完成。")

        await interaction.followup.send("同步開始 - 將已退出群組的資料庫名單進行刪除⋯⋯")
        
        isMoreUser = True
        page = 1
        while isMoreUser:
            Result = UserServiceObject.getAllMemberPaginates(page, 50)
            if Result['result'] is None or len(Result['result']) == 0:
                isMoreUser = False
                continue

            for user in Result['result']:
                # 如果使用者不在伺服器中，則刪除資料庫中的使用者
                print(f"檢查使用者 {user['name']} <@{user['uuid']}> 是否在伺服器中...")
                try:
                    await guild.fetch_member(user['uuid'])
                except discord.NotFound:
                    UserServiceObject.delete(user['uuid'])
                    await interaction.followup.send(f"使用者 {user['name']} <@{user['uuid']}> 已經不在伺服器中，已從資料庫刪除。")
            
            page += 1
        
        await interaction.followup.send("更新完成。")


    # 列出連續未簽到的用戶
    @app_commands.command(name="列表", description=f"列出連續 {executeDays} 天未曾簽到的用戶")
    @RoleService.checkBanned(False)
    @RoleService.checkManager(True)
    async def list(self, interaction: discord.Interaction):
        UserServiceObject = UserService()
        UserServiceObject.firstOrCreate(interaction.user)
        
        # 開始取得列表
        pageSize = 10
        page = 1

        description = "# 以下是目前的不活躍成員清單：\n\n"
        await interaction.response.send_message(content="# 以下是目前的不活躍成員清單：\n\n")
        while True:
            result = UserServiceObject.getInactivePaginates(days=self.executeDays, page=page, page_size=pageSize)
            if (result['result'] is None or len(result['result']) == 0):
                if (page == 1):
                    description += "### 目前沒有任何不活躍成員成員！\n\n"
                break

            for user in result['result']:
                description += f"**{user['id']}.** {user['name']} **<@{user['uuid']}>**\n"
                description += f"> 最後回報簽到任務時間：";
                description += "從未" if user['latest_checkin_at'] is None else user['latest_checkin_at'].strftime("%Y-%m-%d %H:%M:%S")
                description += "\n"
                description += f"> 最後訊息回覆時間：";
                description += "從未" if user['latest_message_at'] is None else user['latest_message_at'].strftime("%Y-%m-%d %H:%M:%S")
                description += "\n\n"

            page += 1
            await interaction.followup.send(content=description)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

async def setup(bot):
    await bot.add_cog(CronInactiveUser(bot))
