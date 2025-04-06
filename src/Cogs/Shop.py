import discord
from discord.ext import commands
from discord import app_commands

from Services.UserService import UserService
from Services.MerchandiseService import MerchandiseService
from Views.PaginationView import PaginationView
from Services.TransferService import TransferService
from Services.RoleService import RoleService

class Shop(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    @app_commands.command(name='查看商品', description='商店街——從逃過羞恥任務的刷新卷，到讓人心跳加速的商品，應有盡有！')
    @app_commands.describe(member="（選填）只想查看特定成員的商品？可以透過這個選項設定你想只查看誰所上架的商品！")
    @RoleService.checkIsNotBanned()
    async def shop(self, interaction: discord.Interaction, member: discord.Member = None):
        UserServiceObject = UserService()
        
        User = UserServiceObject.firstOrCreate(member) if member is not None else None
        UserId = User['id'] if User is not None else None

        L = 10    # elements per page
        async def get_page(view:discord.ui.View, page: int):
            MerchandiseServiceObject = MerchandiseService()
            result = MerchandiseServiceObject.getAllPaginates(UserId , page, L)

            n = PaginationView.compute_total_pages(result['total_count'], L)
            emb = discord.Embed(title="商品清單", description=f"{interaction.user.mention} 您好！\n")

            emb.description += f"這是"
            if member is not None:
                emb.description += f" {member.mention} "
            emb.description += f"目前的商品清單！\n\n"
            emb.description += "====================================\n\n"
            if (len(result['result']) == 0):
                emb.description += "目前沒有任何商品！\n\n"
            else:
                for merchandises in result['result']:
                    emb.description += f"**{merchandises['id']}.** **{merchandises['name']}**"
                    if merchandises["user_name"] is not None:
                        emb.description += f" By **<@{merchandises['uuid']}>**"
                    emb.description += f" - {merchandises['price']} 元\n"

            emb.description += "\n"
            emb.description += "====================================\n\n"
            emb.description += "**使用說明**\n"
            emb.description += "1. 每個商品名稱前，都有一個商品 ID，例如 `1. 任務刷新卷` 的商品 ID 就是 `1` \n"
            emb.description += "2. 透過 `\shop 購買商品` 並輸入對應商品 ID 即可查看完整資訊 \n"
            emb.description += "3. 如果確定要購買，再點下「確認購買」按鈕即可 \n"
            emb.set_author(name=f"Requested by {interaction.user.display_name}")
            emb.set_footer(text=f"Page {page} from {n}")
            return emb, n

        await PaginationView(interaction, get_page).navigate()

    @app_commands.command(name='購買商品')
    @app_commands.describe(merchandise_id="商品 ID")
    @app_commands.describe(quantity="購買數量")
    @RoleService.checkIsNotBanned()
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
        class Button(discord.ui.Button):
            def __init__(self, *args, **kwargs):
                self.User = kwargs.pop('User')
                self.Merchandise = kwargs.pop('Merchandise')
                self.quantity = kwargs.pop('quantity')
                super().__init__(*args, **kwargs)

            async def callback(self, interaction: discord.Interaction) -> None:
                if (self.Merchandise['user_id'] == self.User['id']):
                    await interaction.response.edit_message(content=f"{interaction.user.mention} 您無法購買自己的商品！", view=None)
                    return
                if (int(self.User['balance']) < (int(self.Merchandise['price']) * int(self.quantity))):
                    await interaction.response.edit_message(content=f"{interaction.user.mention} 您的餘額不足，無法購買此商品！", view=None, embed=None)
                    return

                UserServiceObject = UserService()
                ToUser = UserServiceObject.findById(self.Merchandise['user_id'])
                TransferServiceObject = TransferService()
                TransferServiceObject.buyMerchandise(self.User, ToUser, self.Merchandise, self.quantity)

                if (self.Merchandise['uuid'] is not None):
                    message =  "====================================\n"
                    message += "商品賣出通知\n"
                    message += "====================================\n"
                    message += f"購買人： {interaction.user.mention}\n"   
                    message += f"商　品： {self.Merchandise['name']}\n"
                    message += f"單　價： {self.Merchandise['price']} 元\n"
                    message += f"數　量： {self.quantity} 個\n"
                    message += f"合　計： {self.Merchandise['price'] * self.quantity} 元\n"
                    message += f"-# （這筆金額將在對方兌換後，扣除手續費後匯入您的帳戶）"
                    await UserService.sendMessage(
                        bot=interaction.client, 
                        guildId=interaction.guild.id, 
                        uuid=self.Merchandise['uuid'], 
                        message=message
                    )

                self.disabled = True
                await interaction.response.edit_message(content=f'{interaction.user.mention} 您已購買成功！', view=None)


        ButtonObject = Button(
            label="確定購買", 
            style=discord.ButtonStyle.green, 
            disabled=False, 
            row=1, 
            Merchandise=Merchandise, 
            quantity=quantity, 
            User=User
        )
        View = discord.ui.View(timeout=None)
        View.add_item(ButtonObject)
        await interaction.response.send_message(embed=embed, view=View, ephemeral=True)

    @app_commands.command(name='商品上架', description='以你作為販售者，為這個伺服器新增一項新商品！')
    @RoleService.checkIsNotBanned()
    async def merchandiseAvailable(self, interaction: discord.Interaction):
        class MerchandiseModal(discord.ui.Modal, title="商品上架表格"):
            merchandiseName  = discord.ui.TextInput(label="商品名稱", placeholder="請輸入商品名稱", required=True, min_length=1, max_length=255)
            merchandiseDesc  = discord.ui.TextInput(label="商品描述", placeholder="請輸入商品描述", style = discord.TextStyle.paragraph, required=True, min_length=1, max_length=255)
            merchandisePrice  = discord.ui.TextInput(label="商品價格", placeholder="請輸入商品價格", required=True)

            async def on_submit(self, interaction: discord.Interaction):
                if (self.merchandisePrice.value.isnumeric() == False):
                    await interaction.response.send_message(f"{interaction.user.mention} 商品價格必須是數字！", ephemeral=True)
                    return
                if (int(self.merchandisePrice.value) <= 0):
                    await interaction.response.send_message(f"{interaction.user.mention} 商品價格必須大於 0！", ephemeral=True)
                    return
                UserServiceObject = UserService()
                User = UserServiceObject.firstOrCreate(interaction.user)
                MerchandiseServiceObject = MerchandiseService()
                merchandiseId = MerchandiseServiceObject.create(User['id'], {
                    'name': self.merchandiseName.value,
                    'description': self.merchandiseDesc.value,
                    'price': self.merchandisePrice.value
                })

                embed = discord.Embed(title="商品上架成功", description="")
                embed.description = f"# 商品快訊\n\n"
                embed.description += f"{interaction.user.mention} 上架了一則新商品！\n\n"
                embed.add_field(name="商品 ID", value=merchandiseId, inline=True)
                embed.add_field(name="商品名稱", value=f"{self.merchandiseName.value}", inline=False)
                embed.add_field(name="商品描述", value=f"{self.merchandiseDesc.value}", inline=False)
                embed.add_field(name="商品價格", value=f"{self.merchandisePrice.value} 元", inline=False)
                embed.add_field(name="商品擁有者", value=interaction.user.mention, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=False)
                await interaction.followup.send(f"{interaction.user.mention} 商品上架成功！", ephemeral=True)

        # # Modal
        await interaction.response.send_modal(MerchandiseModal())

    @app_commands.command(name='商品下架', description='下架一則屬於你的商品！')
    @app_commands.describe(merchandise_id="商品 ID")
    @RoleService.checkIsNotBanned()
    async def merchandiseUnavailable(self, interaction: discord.Interaction, merchandise_id: int = None):
        class ConfirmButton(discord.ui.Button):
            def __init__(self, *args, **kwargs):
                self.merchandise_id = kwargs.pop('merchandise_id')
                super().__init__(*args, **kwargs)

            async def callback(self, interaction: discord.Interaction):
                Merchandise = MerchandiseServiceObject.findById(self.merchandise_id)
                if (Merchandise is None or Merchandise['deleted_at'] is not None):
                    await interaction.response.edit_message(content=f"{interaction.user.mention} 您查詢的商品不存在！", view=None)
                    return
                elif (str(Merchandise['uuid']) != str(interaction.user.id)):
                    await interaction.response.edit_message(content=f"{interaction.user.mention} 您無法下架別人的商品！", view=None)
                    return

                # 確認下架
                UserServiceObject = UserService()
                User = UserServiceObject.firstOrCreate(interaction.user)
                MerchandiseServiceObject.delete(ids=[Merchandise['id']], user_id=User['id'])
                self.disabled = True
                await interaction.response.edit_message(content=f"{interaction.user.mention} 已為您下架指定的商品～", view=self.view)
                return

        MerchandiseServiceObject = MerchandiseService()
        if (merchandise_id is None):
            await interaction.response.send_message(content=f"{interaction.user.mention} 您沒有選擇任何商品！", ephemeral=True)
            return
    
        Merchandise = MerchandiseServiceObject.findById(merchandise_id)
        if (Merchandise is None or Merchandise['deleted_at'] is not None):
            await interaction.response.send_message(content=f"{interaction.user.mention} 您查詢的商品不存在！")
            return
        elif (str(Merchandise['uuid']) != str(interaction.user.id)):
            await interaction.response.send_message(content=f"{interaction.user.mention} 您無法下架別人的商品！", ephemeral=True)
            return
        
        embed = discord.Embed(title="商品下架確認", description="")
        embed.description = f"{interaction.user.mention} 您好！這是您查詢的商品\n\n"
        embed.description += "-# **使用說明**\n"
        embed.description += "-# 若確定要下架這個商品，\n-# 請點選「確認下架」按鈕。\n\n\n"
        embed.add_field(name="商品 ID", value=merchandise_id, inline=False)
        embed.add_field(name="商品名稱", value=f"{Merchandise['name']}", inline=False)
        embed.add_field(name="商品描述", value=f"{Merchandise['description']}", inline=False)
        embed.add_field(name="商品價格", value=f"{Merchandise['price']} 元", inline=False)
        embed.add_field(name="商品擁有者", value=interaction.user.mention, inline=False)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

        View = discord.ui.View(timeout=None)
        View.add_item(ConfirmButton(label="確認下架", style=discord.ButtonStyle.red, disabled=False, row=1, merchandise_id=merchandise_id))
        await interaction.response.send_message(embed=embed, view=View, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Shop(bot))
