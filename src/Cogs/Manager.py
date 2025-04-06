import os
import discord
from discord.ext import commands
from discord import app_commands, Colour
from Services.RoleService import RoleService
from Services.UserService import UserService
from Services.TransferService import TransferService
from Services.TopicService import TopicService
from Views.PaginationView import PaginationView

class Manager(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    # 金錢發放
    @app_commands.command(name="金錢發放", description="給予用戶金錢")
    @app_commands.describe(user="要給予的用戶", amount="金錢數量", note="給予的理由或備註 - 若沒有則不填")
    @RoleService.checkIsNotBanned()
    @RoleService.checkIsManager()
    async def giveMoney(self, interaction: discord.Interaction, user: discord.Member, amount: int, note: str = None):
        UserServiceObject = UserService()
        AdminUser   = UserServiceObject.firstOrCreate(interaction.user)
        ToUser      = UserServiceObject.firstOrCreate(user)

        TransferServiceObject = TransferService()
        TransferServiceObject.giveMoney(AdminUser, ToUser, amount, note)

        embed = discord.Embed(title="管理方操作", description="", color=Colour.gold())
        embed.add_field(name="發放對象", value=ToUser['name'], inline=False)
        embed.add_field(name="發放金額", value=f"{amount} 元", inline=False)
        if note is not None:
            embed.add_field(name="備註", value=note, inline=False)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_footer(text=f"由 {interaction.user.display_name} 操作")
        await interaction.response.send_message(embed=embed)

    # 金錢扣除
    @app_commands.command(name="金錢扣除", description="扣除用戶帳上金錢 - 若用戶沒有足夠金錢，則會扣除至負數")
    @app_commands.describe(user="要扣除的用戶", amount="金錢數量", note="扣除的理由或備註 - 若沒有則不填")
    @RoleService.checkIsNotBanned()
    @RoleService.checkIsManager()
    async def takeMoney(self, interaction: discord.Interaction, user: discord.Member, amount: int, note: str = None):
        UserServiceObject = UserService()
        AdminUser   = UserServiceObject.firstOrCreate(interaction.user)
        ToUser      = UserServiceObject.firstOrCreate(user)

        TransferServiceObject = TransferService()
        TransferServiceObject.takeMoney(AdminUser, ToUser, amount, note)

        embed = discord.Embed(title="管理方操作", description="", color=Colour.gold())
        embed.add_field(name="扣除對象", value=ToUser['name'], inline=False)
        embed.add_field(name="扣除金額", value=f"{amount} 元", inline=False)
        if note is not None:
            embed.add_field(name="備註", value=note, inline=False)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_footer(text=f"由 {interaction.user.display_name} 操作")
        await interaction.response.send_message(embed=embed)

    # 上架任務
    @app_commands.command(name="上架任務", description="上架任務")
    @RoleService.checkIsNotBanned()
    @RoleService.checkIsManager()
    async def createTopic(self, interaction: discord.Interaction):
        class TopicModal(discord.ui.Modal, title="簽到任務上架表格"):
            description = discord.ui.TextInput(label="任務內容", placeholder="任務內容", required=True, min_length=1, max_length=255)
            reward      = discord.ui.TextInput(label="任務獎勵", placeholder="設定「回報任務後會拿到的錢」", required=False)
            note        = discord.ui.TextInput(label="任務備註", placeholder="提供使用者的備注指示", required=False, min_length=1, max_length=255)

            async def on_submit(self, interaction: discord.Interaction):
                reward = None if (self.reward.value == "" or not self.reward.value.isdigit()) else int(self.reward.value)
                note   = None if self.note.value == "" else self.note.value
                description = self.description.value
                if (reward is not None and reward <= 0):
                    await interaction.response.send_message(f"{interaction.user.mention} 任務獎勵若有設定，則金額必須大於 0！", ephemeral=True)
                    return

                TopicServiceObject = TopicService()
                TopicServiceObject.create({'description': description, 'reward': reward, 'note': note})

                print(f"上架任務 - {interaction.user.name} - {description} - {reward} - {note}")
                embed = discord.Embed(title="任務上架成功", description="", color=Colour.gold())
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
                embed.description = f"# 商品快訊\n\n"
                embed.description += f"{interaction.user.mention} 上架了一則新簽到任務！\n"
                embed.description += f"-# 究竟誰會是第一位受害者呢？\n\n"
                embed.add_field(name="任務內容", value=description, inline=False)
                embed.add_field(name="任務獎勵", value='無' if reward is None else str(reward) + ' 元', inline=False)
                embed.add_field(name="任務備註", value="無" if note is None else note, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=False)
                await interaction.followup.send(f"{interaction.user.mention} 任務上架成功！", ephemeral=True)

        # # Modal
        await interaction.response.send_modal(TopicModal())

    # 任務清單
    @app_commands.command(name="任務清單", description="查看的任務有哪些")
    @RoleService.checkIsNotBanned()
    @RoleService.checkIsManager()
    async def topicList(self, interaction: discord.Interaction):
        L = 10    # elements per page
        async def get_page(view:discord.ui.View, page: int):
            TopicServiceObject = TopicService()
            result = TopicServiceObject.getAllPaginates(page, L)

            n = PaginationView.compute_total_pages(result['total_count'], L)
            emb = discord.Embed(title="任務清單", description=f"{interaction.user.mention} 您好！\n")
            emb.description += f"這是目前的簽到任務清單！\n\n"

            if (len(result['result']) == 0):
                emb.description += "目前沒有任何簽到任務！\n\n"
            else:
                for topic in result['result']:
                    reward = '無' if topic['reward'] is None else str(topic['reward']) + ' 元'
                    note = "無" if topic['note'] is None else topic['note']
                    emb.description += f"{topic['id']}. {topic['description']}\n"
                    emb.description += f"-# 獎勵: {reward} | 備註： {note}\n\n"
            emb.set_author(name=f"{interaction.user.display_name}", icon_url=interaction.user.avatar.url)
            emb.set_footer(text=f"Page {page} from {n}")
            return emb, n

        await PaginationView(interaction, get_page).navigate()

    # 下架任務
    @app_commands.command(name="下架任務", description="給予指定的任務 ID 並將該則任務進行下架")
    @app_commands.describe(topic_id="要下架的任務 ID，請透過「/manager 任務清單」指令查看")
    @RoleService.checkIsNotBanned()
    @RoleService.checkIsManager()
    async def deleteTopic(self, interaction: discord.Interaction, topic_id: int):
        # 會必須把所有進行中尚未結束的任務都更新為 SKIP
        # TopicServiceObject = TopicService()
        # TopicServiceObject.delete([topic_id])
        await interaction.response.defer()

    # 強制下架商品
    async def forceMerchandiseUnavailable(self, interaction: discord.Interaction):
        await interaction.response.defer()

async def setup(bot):
    await bot.add_cog(Manager(bot))
