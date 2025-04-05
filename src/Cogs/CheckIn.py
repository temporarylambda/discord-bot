import os
import discord
from discord.ext import commands
from discord import app_commands

from Services.UserService import UserService
from Services.TopicService import TopicService
from Views.DropdownView import DropdownView
from Services.TransferService import TransferService
from Services.RoleService import RoleService

async def tasksReportCallback(Button: discord.ui.Button, interaction: discord.Interaction):
    Button.disabled = True
    View = Button.view
    Dropdown = Button.view.dropdown

    # 尚未選擇處理
    if (len(Dropdown.values) == 0):
        await interaction.response.edit_message(content=f"{interaction.user.mention} 您沒有選擇任何任務！", view=None)
        return

    User = View.User
    TopicServiceObject = TopicService()
    
    # 防範重複回報
    currentTopics = TopicServiceObject.getCurrentTopics(User['id'], Dropdown.values) # 僅挑選出目前有選擇的任務，查詢他們是否目前正在進行中
    if len(currentTopics) == 0:
        await interaction.response.edit_message(content=f"{interaction.user.mention} 您選擇的任務似乎都已經回報過囉！", view=None)
        return
    
    # 將取得的目前進行中任務跟使用者選擇的任務進行交集，作為實際回報的任務 
    selected_values = set(Dropdown.values) & set([str(topic['id']) for topic in currentTopics])
    selected_values = list(selected_values)

    # 簽到
    TopicServiceObject.complete(User['id'], selected_values)

    # 獎勵金發放
    reward = 0
    TransferServiceObject = TransferService()
    for currentTopic in currentTopics:
        if (str(currentTopic['id']) in selected_values and currentTopic['reward'] is not None and int(currentTopic['reward']) > 0):
            reward += int(currentTopic['reward'])
            TransferServiceObject.giveCheckInReward(currentTopic['id'], User, int(currentTopic['reward']))
    
    await interaction.response.edit_message(content=f"{interaction.user.mention} 回報成功囉！\n您的獎勵也已經發放到您的帳戶了，共計 {reward} 元！", view=None)

class CheckIn(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    @app_commands.command(name='簽到', description='隨機出一則真心話或大挑戰！')
    @RoleService.checkIsNotBanned()
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
        embed = discord.Embed(title="每日簽到！", description=f"{interaction.user.mention} 您好！\n這是您的簽到題目！")
        embed.add_field(name="題目", value=DailyCheckInTopic['description'], inline=False)
        if DailyCheckInTopic['reward'] is not None:
            embed.add_field(name="獎勵", value=f"{DailyCheckInTopic['reward']} 元", inline=False)

        if DailyCheckInTopic['note'] is not None:
            embed.add_field(name="備註", value=DailyCheckInTopic['note'], inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='任務', description='查詢目前你的簽到任務')
    @RoleService.checkIsNotBanned()
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
            if DailyCheckInTopic['reward'] is not None:
                embedDescription += f"\n獎勵：{DailyCheckInTopic['reward']} 元"
            
            if DailyCheckInTopic['note'] is not None:
                embedDescription += f"\n備註：{DailyCheckInTopic['note']}"

        await interaction.response.send_message(embedDescription, ephemeral=True)

    # 呈現下拉選單選擇要回報的任務 - 實際的回報邏輯在 CurrentTopicDropdownView 的 confirm_button 中
    @app_commands.command(name='任務回報', description='完成你的簽到任務來獲得獎勵！')
    @RoleService.checkIsNotBanned()
    async def tasks_report(self, interaction: discord.Interaction):
        # 客製化 Dropdown 下拉選單取得資料
        async def getDataset(self, interaction: discord.Interaction):
            dropdown = None

            TopicServiceObject = TopicService()
            options = TopicServiceObject.getCurrentTopicsDropdownOptions(self.User['id'])
            content = "您好！\n這是您目前的簽到題目！\n請選擇題目並按下「確認回報」來進行回報！" if dropdown is not None else "您目前沒有任何簽到任務！"
            return {
                'content': content,
                'dropdown': DropdownView.generateDropdown(
                    placeholder="請選擇您想回報的簽到任務！", 
                    min_values=1, 
                    max_values=min(int(os.getenv("RULE_CHECK_IN_MAX_TIMES", 1)), len(options)), 
                    options=options
                ) if len(options) > 0 else None
            }

        UserServiceObject = UserService()
        User = UserServiceObject.firstOrCreate(interaction.user)

        DropdownViewObject = DropdownView(
            bot=self.bot, 
            interaction=interaction, 
            User=User, 
            getDatasetCallback=getDataset, 
            ButtonList=[
                DropdownView.generateButton(
                    label="回報任務", 
                    style=discord.ButtonStyle.green, 
                    disabled=False, 
                    row=1, 
                    custom_callback=tasksReportCallback
                )
            ]
        )
        await DropdownViewObject.handler()


async def setup(bot):
    await bot.add_cog(CheckIn(bot))
