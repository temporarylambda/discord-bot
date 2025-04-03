import discord
from Services.UserService import UserService
from Services.TransferService import TransferService
from typing import Callable, Optional

class BuyMerchandiseView(discord.ui.View):
    def __init__(self, merchandise, quantity: int = 1):
        super().__init__()
        self.merchandise = merchandise
        self.quantity = quantity

    @discord.ui.button(label="確定購買", style=discord.ButtonStyle.green, disabled=False, row=1)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        UserServiceObject = UserService()
        FromUser = UserServiceObject.firstOrCreate(interaction.user)
        if (int(FromUser['balance']) < (int(self.merchandise['price']) * int(self.quantity))):
            await interaction.response.edit_message(content=f"{interaction.user.mention} 您的餘額不足，無法購買此商品！", view=None)
            return

        ToUser = UserServiceObject.findById(self.merchandise['user_id'])
        TransferServiceObject = TransferService()
        TransferServiceObject.buyMerchandise(FromUser, ToUser, self.merchandise, self.quantity)

        await interaction.response.edit_message(content=f'{interaction.user.mention} 您已購買成功！', view=None)