import discord
import os
from discord.ext import tasks, commands
from discord import app_commands
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from Services.RoleService import RoleService
from Services.UserService import UserService

class Invite(commands.GroupCog):
    midnightTime = time(hour=0, minute=0, second=0, tzinfo=ZoneInfo("Asia/Taipei"))

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    @app_commands.command(name="邀請", description="產出一則「時效七天、僅可使用一次」的邀請連結！")
    @RoleService.checkBanned(False)
    async def personal_data(self, interaction: discord.Interaction):
        INVITE_CHANNEL_ID = os.getenv("INVITE_CHANNEL_ID")
        if not interaction.guild:
            await interaction.response.send_message("請在伺服器內使用此指令！", ephemeral=True)
            return

        # 取得頻道物件
        text_channel = interaction.guild.get_channel(int(INVITE_CHANNEL_ID))
        if text_channel is None:
            await interaction.response.send_message("伺服器管理員尚未指定入口頻道（設定後需重啟機器人）")
            return

        INVITE_LIFE_TIME_HOUR = os.getenv("INVITE_LIFE_TIME_HOUR")
        timezone    = ZoneInfo("Asia/Taipei")
        timestamp   = discord.utils.utcnow().astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S')
        endtime     = datetime.now(timezone) + timedelta(hours=int(INVITE_LIFE_TIME_HOUR))
        invite = await text_channel.create_invite(
            max_age=int(INVITE_LIFE_TIME_HOUR) * 60 * 60,  # 七天（秒）
            max_uses=1,
            unique=True,
            reason=f"由 {interaction.user.display_name} 使用指令產生 ({timestamp}) - {endtime.strftime('%Y-%m-%d %H:%M:%S')} 到期",
        )

        await interaction.response.send_message(f"{interaction.user.mention}\n🔗 這是你的邀請連結\n - {endtime.strftime('%Y-%m-%d %H:%M:%S')} 到期\n- 僅限一次使用：\n{invite.url}", ephemeral=True)
        await interaction.followup.send(f"🔗 {interaction.user.mention} 透過了一則指令建立了邀請連結！")

async def setup(bot):
    await bot.add_cog(Invite(bot))
