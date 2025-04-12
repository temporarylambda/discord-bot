import os
import discord
from discord.ext import commands
from discord import app_commands
from Services.UserService import UserService
from Services.TransferService import TransferService
from Services.RoleService import RoleService

class Bank(commands.GroupCog):
    transferFee = os.getenv("RULE_TRANSFER_FEE", 15)
    def __init__(self, bot):
        self.bot = bot
        self.transferFee = os.getenv("RULE_TRANSFER_FEE", 15)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    @app_commands.command(name='轉帳', description=f'轉帳給指定的成員！（轉帳費 {transferFee} 元）')
    @app_commands.describe(member="把錢給這個人")
    @app_commands.describe(amount="轉帳金額")
    @RoleService.checkBanned(False)
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        UserServiceObject = UserService()
        FromUser = UserServiceObject.firstOrCreate(interaction.user)
        ToUser = UserServiceObject.firstOrCreate(member)
        totalAmount = int(amount) + int(self.transferFee)
        if (ToUser is None):
            await interaction.response.send_message(f"{interaction.user.mention} 抱歉！您轉帳的對象 {member.mention} 並不存在！", ephemeral=True)
            return
        elif (ToUser['uuid'] == FromUser['uuid']):
            await interaction.response.send_message(f"{interaction.user.mention} 抱歉！您不能轉帳給自己！", ephemeral=True)
            return
        elif (FromUser['balance'] < int(amount) + int(self.transferFee)):
            message  = f"{interaction.user.mention}抱歉！您的餘額不足，無法轉帳給 {member.mention} {amount} 元！\n"
            message += f"轉帳需要至少包含手續費 {self.transferFee} 元，合計 {totalAmount} 元\n"
            message += f"您目前只有 {FromUser['balance']} 元\n"

            await interaction.response.send_message(message, ephemeral=True)
            return

        TransferServiceObject = TransferService()
        transferResult = TransferServiceObject.transfer(FromUser=FromUser, ToUser=ToUser, amount=amount)

        # 轉帳完畢後重新撈取一次最新的使用者資料（取得轉帳後餘額）
        FromUser = UserServiceObject.firstOrCreate(interaction.user)
        ToUser   = UserServiceObject.firstOrCreate(member)
        
        message =  "===================================\n"
        message += "轉帳通知 - 金額已轉入您的帳戶\n"
        message += "===================================\n"
        message += f"轉帳人： {interaction.user.mention}\n"   
        message += f"金　額： {transferResult['amount']} 元\n"
        message += f"手續費： {transferResult['fee']} 元\n"
        message += f"實　收： {transferResult['final_amount']} 元\n"
        message += f"餘　額： {ToUser['balance']} 元\n"
        await UserService.sendMessage(self.bot, interaction.guild.id, ToUser['uuid'], message)

        message =  "===================================\n"
        message += f"轉帳通知 - 金額已轉入 <@{ToUser['uuid']}> 的帳戶\n"
        message += "===================================\n"
        message += f"收受人： <@{ToUser['uuid']}>\n"   
        message += f"金　額： {transferResult['amount']} 元\n"
        message += f"手續費： {transferResult['fee']} 元\n"
        message += f"實　收： {transferResult['final_amount']} 元\n"
        message += f"餘　額： {FromUser['balance']} 元\n"
        await UserService.sendMessage(self.bot, interaction.guild.id, FromUser['uuid'], message)
        await interaction.response.send_message(f"{interaction.user.mention} 已經轉帳給 {member.mention} {amount} 元！", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Bank(bot))
