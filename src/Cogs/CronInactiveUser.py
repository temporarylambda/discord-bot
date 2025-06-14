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
        

    # 同步目前尚未建立資料庫資料的群組成員
    @app_commands.command(name="同步", description="同步目前所有已加入群組但因為未曾操作過機器人所以在資料庫尚未有資料的群組成員")
    @RoleService.checkBanned(False)
    @RoleService.checkManager(True)
    async def sync(self, interaction: discord.Interaction):
        await interaction.response.send_message("開始同步所有成員資料！")
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
        
        await interaction.channel.send("已同步所有成員資料！")


    # 列出連續未簽到的用戶
    @app_commands.command(name="列表", description=f"列出連續 {executeDays} 天未曾簽到的用戶")
    @RoleService.checkBanned(False)
    @RoleService.checkManager(True)
    async def list(self, interaction: discord.Interaction):
        UserServiceObject = UserService()
        UserServiceObject.firstOrCreate(interaction.user)
        
        # 開始取得列表
        L = 10    # elements per page
        async def get_page(view:discord.ui.View, page: int):
            result = UserServiceObject.getInactivePaginates(days=self.executeDays, page=page, page_size=L)

            n = PaginationView.compute_total_pages(result['total_count'], L)
            emb = discord.Embed(title="不活躍成員清單", description=f"{interaction.user.mention} 您好！")

            emb.description += f"這是目前的不活躍成員清單！\n\n"
            if (len(result['result']) == 0):
                emb.description += "# 目前沒有任何不活躍成員成員！\n\n"
            else:
                for user in result['result']:
                    emb.description += f"**{user['id']}.** **<@{user['uuid']}>**\n"
                    emb.description += f"> 最後回報簽到任務時間：";
                    emb.description += "從未" if user['latest_checkin_at'] is None else user['latest_checkin_at'].strftime("%Y-%m-%d %H:%M:%S")
                    emb.description += "\n\n"

            emb.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            emb.set_footer(text=f"Page {page} from {n}")
            return emb, n

        await PaginationView(interaction, get_page).navigate()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

async def setup(bot):
    await bot.add_cog(CronInactiveUser(bot))
