import discord
from discord.ext import commands
from discord import app_commands

from Services.UserService import UserService
from Services.TopicService import TopicService
from Views.CurrentTopicDropdownView import CurrentTopicDropdownView


class CheckIn(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    @app_commands.command(name='簽到', description='隨機出一則真心話或大挑戰！')
    async def daily_check_in(self, interaction: discord.Interaction):
        UserServiceObject = UserService()
        User = UserServiceObject.firstOrCreate(interaction.user)

        TopicServiceObject = TopicService()
        if TopicServiceObject.isUnavailable(User['id']):
            await interaction.response.send_message(f"{interaction.user.mention} 您目前沒有額度可以領取新的簽到題目，請先完成手上的題目再來簽到！", ephemeral=True)
            return
        elif TopicServiceObject.isTodayTaken(User['id']):
            await interaction.response.send_message(f"{interaction.user.mention} 今天您已經領取完所有可以領取的題目了！", ephemeral=True)
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

    @app_commands.command(name='任務', description='查詢目前你的簽到任務')
    async def tasks(self, interaction: discord.Interaction):
        UserServiceObject = UserService()
        User = UserServiceObject.firstOrCreate(interaction.user)

        TopicServiceObject = TopicService()
        DailyCheckInTopics = TopicServiceObject.getCurrentTopics(User['id'])
        if len(DailyCheckInTopics) == 0:
            await interaction.response.send_message(f"{interaction.user.mention} 您目前沒有任何簽到任務！", ephemeral=True)
            return

        embedDescription = f"# 簽到任務查詢\n{interaction.user.mention} 您好！\n這是您的簽到任務！"
        for DailyCheckInTopic in DailyCheckInTopics:
            embedDescription += f"\n\n題目：{DailyCheckInTopic['description']}"
            if DailyCheckInTopic['reward'] and str(DailyCheckInTopic['reward']).isdigit() and int(DailyCheckInTopic['reward']) > 0:
                embedDescription += f"\n獎勵：{DailyCheckInTopic['reward']} 元"
            
            if DailyCheckInTopic['note'] is not None:
                embedDescription += f"\n備註：{DailyCheckInTopic['note']}"

        await interaction.response.send_message(embedDescription)

    # 呈現下拉選單選擇要回報的任務 - 實際的回報邏輯在 CurrentTopicDropdownView 的 confirm_button 中
    @app_commands.command(name='任務回報', description='完成你的簽到任務來獲得獎勵！')
    async def tasks_report(self, interaction: discord.Interaction):
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


async def setup(bot):
    await bot.add_cog(CheckIn(bot))
