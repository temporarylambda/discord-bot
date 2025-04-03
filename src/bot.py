from Services.UserService import UserService
from Services.TopicService import TopicService
from Services.MerchandiseService import MerchandiseService
from Views.PaginationView import PaginationView
from Views.CurrentTopicDropdownView import CurrentTopicDropdownView
from Views.BuyMerchandiseView import BuyMerchandiseView
from Services.DatabaseConnection import DatabaseConnection
import os
import discord
from discord import app_commands

MY_GUILD = discord.Object(id=os.getenv("DISCORD_GUILD_ID"))  # 替換為你的伺服器 ID
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.synced = False

    async def setup_hook(self):
        if (not self.synced):
            await self.tree.sync()
            self.synced = True

client = MyClient()

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id}), 本地時間 {DatabaseConnection.getCurrentTimestamp()}')
    print('------')

# 查看目前個人金額與簽到連勝
@client.tree.command(name='個人資料', description='查詢個人資料')
async def personal_data(interaction: discord.Interaction,):
    UserServiceObject = UserService();
    User = UserServiceObject.firstOrCreate(user=interaction.user);

    embed = discord.Embed(title="個人資料查詢", description=f"{interaction.user.mention} 您好！\n這是您的個人資料！")
    embed.add_field(name="錢包餘額", value=f"{User['balance']} 元", inline=False)
    embed.add_field(name="連續簽到連勝", value=f"{User['consecutive_checkin_days']} 日", inline=False)
    await interaction.response.send_message(embed=embed)

# 取得新的簽到題目
@client.tree.command(name='簽到', description='隨機出一則真心話或大挑戰！')
async def daily_check_in(interaction: discord.Interaction):
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

# 查看目前手上的簽到題目
@client.tree.command(name='任務', description='查詢目前你的簽到任務')
async def tasks(interaction: discord.Interaction):
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

# 呈現下拉選單選擇要回報的任務
""" 
實際的回報邏輯在 CurrentTopicDropdownView 的 confirm_button 中
"""
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

@client.tree.command(name='查看商品', description='商店街——從逃過羞恥任務的刷新卷，到讓人心跳加速的商品，應有盡有！')
async def shop(interaction: discord.Interaction, member: discord.Member = None):
    UserServiceObject = UserService()
    
    User = UserServiceObject.firstOrCreate(member) if member is not None else None
    UserId = User['id'] if User is not None else None

    L = 10    # elements per page
    async def get_page(page: int):
        MerchandiseServiceObject = MerchandiseService()
        result = MerchandiseServiceObject.getAll(UserId , page, L)

        n = PaginationView.compute_total_pages(result['total_count'], L)
        emb = discord.Embed(title="商品清單", description=f"{interaction.user.mention} 您好！\n")

        emb.description += f"這是"
        if member is not None:
            emb.description += f" {member.mention} "
        emb.description += f"目前的商品清單！\n\n"

        if (len(result['result']) == 0):
            emb.description += "目前沒有任何商品！\n\n"
        else:
            for merchandises in result['result']:
                emb.description += f"**{merchandises['id']}.** **{merchandises['name']}**"
                if merchandises["user_name"] is not None:
                    emb.description += f" By **{merchandises['user_name']}**"
                emb.description += f" - {merchandises['price']} 元\n"

        emb.description += "\n"
        emb.set_author(name=f"Requested by {interaction.user.display_name}")
        emb.set_footer(text=f"Page {page} from {n}")
        return emb, n

    await PaginationView(interaction, get_page).navegate()

@client.tree.command(name='購買商品', description='商店街——從逃過羞恥任務的刷新卷，到讓人心跳加速的商品，應有盡有！')
@app_commands.describe(merchandise_id="商品 ID")
@app_commands.describe(quantity="購買數量")
async def item(interaction: discord.Interaction, merchandise_id: int, quantity: int = 1):
    UserServiceObject = UserService()
    User = UserServiceObject.firstOrCreate(interaction.user)

    MerchandiseServiceObject = MerchandiseService()
    Merchandise = MerchandiseServiceObject.findById(merchandise_id)

    # 商品不存在
    if Merchandise is None:
        await interaction.response.send_message(f"{interaction.user.mention} 您查詢的商品不存在！")
        return

    # 無法購買自己的商品
    if Merchandise['user_id'] == User['id']:
        await interaction.response.send_message(f"{interaction.user.mention} 您不能購買自己的商品！")
        return

    embed = discord.Embed(title="商品資訊", description="")
    embed.description  = f"{interaction.user.mention} 您好！這是您查詢的商品\n\n"
    embed.add_field(name="商品 ID", value=merchandise_id, inline=False)
    embed.add_field(name="商品名稱", value=f"{Merchandise['name']}", inline=False)
    embed.add_field(name="商品描述", value=f"{Merchandise['description']}", inline=False)
    embed.add_field(name="商品價格", value=f"{Merchandise['price']} 元", inline=False)
    embed.add_field(name="商品擁有者", value=Merchandise['user_name'] if Merchandise['user_name'] is not None else "系統", inline=False)
    embed.add_field(name="購買數量", value=f"{quantity} 個", inline=False)
    embed.add_field(name="合計總價", value=f"{Merchandise['price'] * quantity} 元", inline=False)

    # 加上按鈕
    BuyMerchandiseViewObject = BuyMerchandiseView(Merchandise, quantity)
    await interaction.response.send_message(embed=embed, view=BuyMerchandiseViewObject, ephemeral=True)


client.run(os.getenv("DISCORD_BOT_TOKEN"))
