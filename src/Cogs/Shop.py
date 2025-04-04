import discord
from discord.ext import commands
from discord import app_commands

from Services.UserService import UserService
from Services.MerchandiseService import MerchandiseService
from Views.PaginationView import PaginationView
from Views.BuyMerchandiseView import BuyMerchandiseView


class Shop(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    @app_commands.command(name='查看商品', description='商店街——從逃過羞恥任務的刷新卷，到讓人心跳加速的商品，應有盡有！')
    @app_commands.describe(member="（選填）只想查看特定成員的商品？可以透過這個選項設定你想只查看誰所上架的商品！")
    async def shop(self, interaction: discord.Interaction, member: discord.Member = None):
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

    @app_commands.command(name='購買商品')
    @app_commands.describe(merchandise_id="商品 ID")
    @app_commands.describe(quantity="購買數量")
    async def item(self, interaction: discord.Interaction, merchandise_id: int, quantity: int = 1):
        UserServiceObject = UserService()
        User = UserServiceObject.firstOrCreate(interaction.user)

        MerchandiseServiceObject = MerchandiseService()
        Merchandise = MerchandiseServiceObject.findById(merchandise_id)

        # 商品不存在
        if Merchandise is None:
            await interaction.response.send_message(f"{interaction.user.mention} 您查詢的商品不存在！", ephemeral=True)
            return

        # 無法購買自己的商品
        if Merchandise['user_id'] == User['id']:
            await interaction.response.send_message(f"{interaction.user.mention} 您不能購買自己的商品！", ephemeral=True)
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

async def setup(bot):
    await bot.add_cog(Shop(bot))
