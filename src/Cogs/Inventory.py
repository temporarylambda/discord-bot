import discord
from discord.ext import commands
from discord import app_commands

from Services.UserService import UserService
from Views.PaginationView import PaginationView
from Services.UserInventoryService import UserInventoryService
from Services.TransferService import TransferService
from Services.TopicService import TopicService
from Enums.MerchandiseSystemType import MerchandiseSystemType
from Services.RoleService import RoleService

# 通常商品兌換邏輯 - 撥款給上架人並發送私訊給上架人
async def normalMerchandiseRedeemCallback(User: dict, interaction: discord.Interaction, UserInventoryServiceObject: UserInventoryService, Inventory: dict):
    # 撥款給上架人
    TransferServiceObject = TransferService()
    redeemResult = TransferServiceObject.redeemMerchandise(User=User, Inventory=Inventory)

    # 更新 UserInventory 對應資料的使用狀態，並記錄 redeemed_at 時間
    UserInventoryServiceObject.redeem(Inventory['id'])

    # # 發送 Direct Message 給上架者，告知兌換者的資訊
    merchant_uuid = Inventory['uuid']
    if merchant_uuid is not None:
        message =  "===================================\n"
        message += "商品兌換通知 - 金額已轉入您的帳戶\n"
        message += "===================================\n"
        message += f"購買人： {interaction.user.mention}\n"   
        message += f"商　品： {Inventory['name']}\n"
        message += f"單　價： {redeemResult['price']} 元\n"
        message += f"手續費： {redeemResult['fee']} 元\n"
        message += f"實　收： {redeemResult['final_price']} 元\n"
        await UserService.sendMessage(bot=interaction.client, guildId=interaction.guild.id, uuid=merchant_uuid, message=message)

    await interaction.response.edit_message(content=f"{interaction.user.mention} 您已成功兌換了 {Inventory['name']}，相關費用已經發放到對方戶頭！", view=None)

class Inventory(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    @app_commands.command(name='查看背包', description='查看目前擁有的未兌換商品有哪些！')
    async def inventory(self, interaction: discord.Interaction):
        UserServiceObject = UserService()
        
        User = UserServiceObject.firstOrCreate(interaction.user)
        UserId = User['id'] if User is not None else None

        L = 10    # elements per page
        async def get_page(view: discord.ui.View, page: int):
            UserInventoryServiceObject = UserInventoryService()
            result = UserInventoryServiceObject.getAll(UserId , page, L)
            print(result)

            n = PaginationView.compute_total_pages(result['total_count'], L)
            emb = discord.Embed(title="背包清單", description=f"{interaction.user.mention} 您好！\n這是您目前尚未兌換的商品！\n\n")

            if (len(result['result']) == 0):
                emb.description += "目前沒有任何商品！\n\n"
            else:
                for index, merchandises in enumerate(result['result']):
                    emb.description += f"**{merchandises['merchandise_id']}.** **{merchandises['name']}**"
                    emb.description += '' if merchandises["uuid"] is None else f" (By **<@{merchandises['uuid']}>)**"
                    emb.description += f" - {merchandises['quantity']} 個\n"

            emb.description += "\n"
            emb.set_author(name=f"Requested by {interaction.user.display_name}")
            emb.set_footer(text=f"Page {page} from {n}")
            return emb, n

        await PaginationView(interaction, get_page).navegate()

    # TODO: 下拉選單超過 25 個選項 Discord 會跳錯誤，所以這邊應該要調整成「輸入 merchandise_id」的方式來兌換商品
    @app_commands.command(name='兌換商品', description='輸入對應的商品 ID 來兌換背包中的商品！（一次兌換一個）')
    @app_commands.describe(merchandise_id="商品 ID")
    @RoleService.checkIsNotBanned()
    async def redeem(self, interaction: discord.Interaction, merchandise_id: int = None):
        if (merchandise_id is None):
            await interaction.response.send_message(content=f"{interaction.user.mention} 您沒有輸入任何商品 ID！", ephemeral=True)
            return
        
        UserInventoryServiceObject = UserInventoryService()
        UserServiceObject = UserService()
        User = UserServiceObject.firstOrCreate(interaction.user)
    
        # 取得使用者選擇的商品資料
        Inventory = None
        if merchandise_id is not None:
            Inventory = UserInventoryServiceObject.firstByMerchandiseId(User['id'], merchandise_id)

        # 商品不存在
        if Inventory is None:
            await interaction.response.send_message(content=f"{interaction.user.mention} 您的背包裡沒有該項商品可供兌換！", ephemeral=True)
            return
        
        # 任務刷新卷
        elif Inventory['system_type'] == MerchandiseSystemType.SYSTEM_CHECK_IN_REFRESH.value:
            await self.__topicRefreshMerchandiseRedeemCallback(User=User, interaction=interaction, UserInventoryServiceObject=UserInventoryServiceObject, Inventory=Inventory)
            return
        
        # 其他特殊用途商品
        elif Inventory['system_type'] is not None:
            await interaction.response.send_message(content=f"{interaction.user.mention} 此為特殊用途商品，不需兌換！", ephemeral=True)
            return
        
        # 通常商品
        else: # 通常商品兌換邏輯 - 撥款給上架人並發送私訊給上架人
            await self.__normalMerchandiseRedeemCallback(User=User, interaction=interaction, UserInventoryServiceObject=UserInventoryServiceObject, Inventory=Inventory)
            return
    
    # 刷新任務卷兌換邏輯 - 提供 Select 選單讓使用者選擇要刷新的任務
    async def __topicRefreshMerchandiseRedeemCallback(self, User:dict, interaction: discord.Interaction, UserInventoryServiceObject:UserInventoryService, Inventory:dict):
        # 生成下拉選單
        class Dropdown(discord.ui.Select):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.defer()

        # 生成確定刷新按鈕
        class RedeemButton(discord.ui.Button):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            async def callback(self, interaction: discord.Interaction):
                if (len(self.view.dropdown.values) == 0):
                    await interaction.response.edit_message(content=f"{interaction.user.mention} 您沒有選擇任何任務！", view=None)
                    return

                # 檢查是否選擇了已經回報完的任務
                TopicServiceObject = TopicService()
                currentTopics = TopicServiceObject.getCurrentTopics(View.User['id'], self.view.dropdown.values) # 僅挑選出目前有選擇的任務，查詢他們是否目前正在進行中
                if len(currentTopics) == 0:
                    await interaction.response.edit_message(content=f"{interaction.user.mention} 您選擇的任務似乎都已經回報過囉！", view=None)
                    return
                
                # 將取得的目前進行中任務跟使用者選擇的任務進行交集，作為實際回報的任務 
                selected_values = set(self.view.dropdown.values) & set([str(topic['id']) for topic in currentTopics])
                selected_values = list(selected_values)

                # 撥款給上架人 - 即使上架人是系統仍然要寫入這樣的紀錄
                TransferServiceObject = TransferService()
                TransferServiceObject.redeemMerchandise(User=View.User, Inventory=Inventory, dailyCheckInTopicIds=selected_values)

                # 更新 UserInventory 對應資料的使用狀態，並記錄 redeemed_at 時間
                UserInventoryServiceObject.redeem(Inventory['id'])
                await interaction.response.edit_message(content=f"{interaction.user.mention} 您的任務已經刷新！", view=None)

        TopicServiceObject = TopicService()
        options = TopicServiceObject.getCurrentTopicsDropdownOptions(User['id'])
        if (len(options) == 0):
            await interaction.response.send_message(content=f"{interaction.user.mention} 您目前沒有任何任務可以進行刷新！", view=None, ephemeral=True)
            return
        
        ConfirmButton = RedeemButton(label="確定刷新", style=discord.ButtonStyle.green, row=1)
        Select = Dropdown(placeholder="請選擇您想要刷新的任務！", min_values=1, max_values=1, options=options)
        View = discord.ui.View(timeout=None)
        View.dropdown = Select
        View.User = User
        View.add_item(Select)
        View.add_item(ConfirmButton)
        await interaction.response.send_message(content=f"{interaction.user.mention} 請選擇你想刷新的任務！", view=View, ephemeral=True)

    async def __normalMerchandiseRedeemCallback(self, User:dict, interaction: discord.Interaction, UserInventoryServiceObject:UserInventoryService, Inventory:dict):
        print("normalMerchandiseRedeemCallback")
        # 撥款給上架人
        TransferServiceObject = TransferService()
        redeemResult = TransferServiceObject.redeemMerchandise(User=User, Inventory=Inventory)

        # 更新 UserInventory 對應資料的使用狀態，並記錄 redeemed_at 時間
        UserInventoryServiceObject.redeem(Inventory['id'])

        # # 發送 Direct Message 給上架者，告知兌換者的資訊
        merchant_uuid = Inventory['uuid']
        if merchant_uuid is not None:
            message =  "===================================\n"
            message += "商品兌換通知 - 金額已轉入您的帳戶\n"
            message += "===================================\n"
            message += f"購買人： {interaction.user.mention}\n"   
            message += f"商　品： {Inventory['name']}\n"
            message += f"單　價： {redeemResult['price']} 元\n"
            message += f"手續費： {redeemResult['fee']} 元\n"
            message += f"實　收： {redeemResult['final_price']} 元\n"
            await UserService.sendMessage(bot=interaction.client, guildId=interaction.guild.id, uuid=merchant_uuid, message=message)

        await interaction.response.send_message(content=f"{interaction.user.mention} 您已成功兌換了 {Inventory['name']}，相關費用已經發放到對方戶頭！", view=None, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Inventory(bot))
