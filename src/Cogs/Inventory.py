import discord
from discord.ext import commands
from discord import app_commands

from Services.UserService import UserService
from Views.PaginationView import PaginationView
from Services.UserInventoryService import UserInventoryService

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


async def setup(bot):
    await bot.add_cog(Inventory(bot))
