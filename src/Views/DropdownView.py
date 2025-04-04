import discord
from typing import Callable

class DropdownView(discord.ui.View):
    def __init__(self, bot, interaction: discord.Interaction, User: dict, getDatasetCallback: Callable, ButtonList: list = [], ephemeral: bool = True):
        super().__init__()
        self.content = ""
        self.dropdown = None

        self.bot = bot
        self.interaction = interaction
        self.User = User
        self.getDatasetCallback = getDatasetCallback
        self.ButtonList = ButtonList
        self.ephemeral = ephemeral

    async def handler(self):
        interaction = self.interaction
        result = await self.getDatasetCallback(self, self.interaction)
        self.content  = result.get("content", "")
        self.dropdown = result.get("dropdown", None)
        if self.dropdown is not None:
            self.add_item(self.dropdown)
            for button in self.ButtonList:
                self.add_item(button)
        
        if (self.dropdown is None):
            await interaction.response.send_message(f"{interaction.user.mention} {self.content}", ephemeral=self.ephemeral)
        else:
            await interaction.response.send_message(f"{interaction.user.mention} {self.content}", view=self, ephemeral=self.ephemeral)

    @staticmethod
    def generateDropdown(*args, **kwargs):
        class Dropdown(discord.ui.Select):
            def __init__(self, *args, **kwargs):
                self.custom_callback = None
                if 'custom_callback' in kwargs:
                    self.custom_callback = kwargs.pop('custom_callback')

                super().__init__(*args, **kwargs)
            
            async def callback(self, interaction: discord.Interaction):
                if self.custom_callback is not None:
                    await self.custom_callback(self, interaction)
                else:
                    await interaction.response.defer()
        
        return Dropdown(*args, **kwargs)

    @staticmethod
    def generateButton(*args, **kwargs):
        class Button(discord.ui.Button):
            def __init__(self, *args, **kwargs):
                self.custom_callback = None
                if 'custom_callback' in kwargs:
                    self.custom_callback = kwargs.pop('custom_callback')
                
                super().__init__(*args, **kwargs)

            async def callback(self, interaction: discord.Interaction):
                if self.custom_callback is not None:
                    await self.custom_callback(self, interaction)
                else:
                    await interaction.response.defer()
        
        return Button(*args, **kwargs)