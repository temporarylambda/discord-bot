import discord
from discord.ext import commands
from discord import app_commands

from Services.UserService import UserService
from Views.PaginationView import PaginationView
from Services.UserInventoryService import UserInventoryService
from Services.TransferService import TransferService
from Views.DropdownView import DropdownView

async def redeemCallback(Button: discord.ui.Button, interaction: discord.Interaction):
    Button.disabled = True
    dropdown = Button.view.dropdown

    UserInventoryServiceObject = UserInventoryService()

    # 取得使用者選擇的商品 ID
    merchandise_id = dropdown.values[0] if len(dropdown.values) > 0 else None
    if merchandise_id is None:
        await interaction.response.edit_message(content=f"{interaction.user.mention} 您沒有選擇任何商品！", view=None)
        return

    # 取得使用者選擇的商品資料
    Inventory = None
    if merchandise_id is not None:
        Inventory = UserInventoryServiceObject.firstByMerchandiseId(Button.view.User['id'], merchandise_id)
    
    # 商品不存在
    if Inventory is None:
        await interaction.response.edit_message(content=f"{interaction.user.mention} 您的背包裡沒有該項商品可供兌換！", view=None)
        return
    
    # 無法兌換自己的商品
    elif Inventory['system_type'] is not None:
        await interaction.response.edit_message(content=f"{interaction.user.mention} 此為特殊用途商品，不需兌換！", view=None)
        return
    
    # # 撥款給上架人
    TransferServiceObject = TransferService()
    redeemResult = TransferServiceObject.redeemMerchandise(User=Button.view.User, Inventory=Inventory)

    # 更新 UserInventory 對應資料的使用狀態，並記錄 redeemed_at 時間
    UserInventoryServiceObject.redeem(Inventory['id'])
    redeemResult = {
        'price': Inventory['price'],
        'fee': int(Inventory['price'] * 0.2),
        'final_price': int(Inventory['price']) - int(Inventory['price'] * 0.2),
    }

    # # 發送 Direct Message 給上架者，告知兌換者的資訊
    merchant_uuid = Inventory['merchant_uuid']
    if merchant_uuid is not None:
        bot = Button.view.bot
        guild = bot.get_guild(interaction.guild.id) # 取得伺服器物件
        user  = guild.get_member(merchant_uuid) or await bot.fetch_user(merchant_uuid) # 從伺服器快取取得使用者物件, 若找不到則從 API 取得
        message = f"{interaction.user.mention} 兌換了您的商品 - {Inventory['name']}，\n原價 {redeemResult['price']} 元，扣除手續費 {redeemResult['fee']} 元後，金額 {redeemResult['final_price']} 元已經轉入您的帳戶！"
        async def send_message(user, message): # 宣告一個 function 來發送訊息
            await user.send(message)
        bot.loop.create_task(send_message(user, message)) # 使用 create_task 來非同步發送訊息

    
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
        async def get_page(page: int):
            UserInventoryServiceObject = UserInventoryService()
            result = UserInventoryServiceObject.getAll(UserId , page, L)
            print(result)

            n = PaginationView.compute_total_pages(result['total_count'], L)
            emb = discord.Embed(title="背包清單", description=f"{interaction.user.mention} 您好！\n這是您目前尚未兌換的商品！\n\n")

            if (len(result['result']) == 0):
                emb.description += "目前沒有任何商品！\n\n"
            else:
                for index, merchandises in enumerate(result['result']):

                    emb.description += f"**{index + 1}.** **{merchandises['name']}**"
                    if merchandises["merchant_name"] is not None:
                        emb.description += f" (By **{merchandises['merchant_name']})**"
                    emb.description += f" - {merchandises['quantity']} 個\n"

            emb.description += "\n"
            emb.set_author(name=f"Requested by {interaction.user.display_name}")
            emb.set_footer(text=f"Page {page} from {n}")
            return emb, n

        await PaginationView(interaction, get_page).navegate()

    @app_commands.command(name='兌換商品', description='兌換背包中的商品！')
    async def redeem(self, interaction: discord.Interaction):
        # 客製化 Dropdown 下拉選單取得資料
        async def getDataset(self, interaction: discord.Interaction):
            dropdown = None
            UserInventoryServiceObject = UserInventoryService()
            result = UserInventoryServiceObject.getAll(self.User['id'], 1, None)
            if (len(result['result']) > 0):
                options = []
                for index, merchandises in enumerate(result['result']):
                    merchant_name = f" (by {merchandises['merchant_name']})" if merchandises['merchant_name'] is not None else ""
                    options.append(discord.SelectOption(label=f"{merchandises['name']}{merchant_name}", value=f"{merchandises['merchandise_id']}", description=f"目前擁有 {merchandises['quantity']} 個"))

                dropdown = DropdownView.generateDropdown(placeholder="請選擇您想兌換的商品！", min_values=1, max_values=1, options=options)
            return {
                'content': "請選擇您想兌換的商品！" if dropdown is not None else "您目前沒有任何商品可以兌換！",
                'dropdown': dropdown
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
                    label="兌換商品", 
                    style=discord.ButtonStyle.green, 
                    disabled=False, 
                    row=1, 
                    custom_callback=redeemCallback
                )
            ]
        )
        await DropdownViewObject.handler()


async def setup(bot):
    await bot.add_cog(Inventory(bot))
