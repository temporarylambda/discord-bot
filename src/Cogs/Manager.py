import os
import discord
from discord.ext import commands
from discord import app_commands, Colour
from Services.RoleService import RoleService
from Services.UserService import UserService
from Services.TransferService import TransferService
from Services.TopicService import TopicService
from Services.MerchandiseService import MerchandiseService
from Enums.MerchandiseSystemType import MerchandiseSystemType
from Views.PaginationView import PaginationView

class Manager(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot
        self.UserService = UserService()
        self.TransferService = TransferService()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" |---- {self.__class__.__name__} 已經載入！")

    # 金錢發放
    @app_commands.command(name="金錢發放", description="給予用戶金錢")
    @app_commands.describe(user="要給予的用戶", amount="金錢數量", note="給予的理由或備註 - 若沒有則不填")
    @RoleService.checkBanned(False)
    @RoleService.checkManager(True)
    async def giveMoney(self, interaction: discord.Interaction, user: discord.Member, amount: int, note: str = None):
        AdminUser = self.UserService.firstOrCreate(interaction.user)
        ToUser    = self.UserService.firstOrCreate(user)
        self.TransferService.transfer(
            ToUser=ToUser,
            FromUser=None,
            amount=amount,
            reason=note if note is not None else f"{AdminUser['name']} 給予 {ToUser['name']} 金額 {amount} 元"
        )

        embed = discord.Embed(title="管理方操作", description="金額發放", color=Colour.gold())
        embed.add_field(name="發放對象", value=ToUser['name'], inline=False)
        embed.add_field(name="發放金額", value=f"{amount} 元", inline=False)
        if note is not None:
            embed.add_field(name="備註", value=note, inline=False)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_footer(text=f"由 {interaction.user.display_name} 操作")

        # 取得發放金額後的最新狀態
        ToUser = self.UserService.firstOrCreate(user)
        message =  "====================================\n"
        message += "管理方操作 - 金額發放\n"
        message += "====================================\n"
        message += f"發放人： {interaction.user.mention}\n"   
        message += f"金　額： {amount} 元\n"
        message += f"備　註： {note} \n" if note is not None else ""
        message += f"餘　額： {ToUser['balance']} 元\n"
        message += f"-# （若有疑慮，請操作客服單取向管理員聯繫）"
        await UserService.sendMessage(self.bot, interaction.guild.id, ToUser['uuid'], message)
        await interaction.response.send_message(embed=embed)

    # 金錢扣除
    @app_commands.command(name="金錢扣除", description="扣除用戶帳上金錢 - 若用戶沒有足夠金錢，則會扣除至負數")
    @app_commands.describe(user="要扣除的用戶", amount="金錢數量", note="扣除的理由或備註 - 若沒有則不填")
    @RoleService.checkBanned(False)
    @RoleService.checkManager(True)
    async def takeMoney(self, interaction: discord.Interaction, user: discord.Member, amount: int, note: str = None):
        AdminUser = self.UserService.firstOrCreate(interaction.user)
        FromUser  = self.UserService.firstOrCreate(user)
        self.TransferService.transfer(
            ToUser=None,
            FromUser=FromUser,
            amount=amount,
            reason=note if note is not None else f"{AdminUser['name']} 扣除 {FromUser['name']} 金額 {amount} 元"
        )

        embed = discord.Embed(title="管理方操作", description="金額扣除", color=Colour.gold())
        embed.add_field(name="扣除對象", value=FromUser['name'], inline=False)
        embed.add_field(name="扣除金額", value=f"{amount} 元", inline=False)
        if note is not None:
            embed.add_field(name="備註", value=note, inline=False)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_footer(text=f"由 {interaction.user.display_name} 操作")

        # 取得發放金額後的最新狀態
        FromUser = self.UserService.firstOrCreate(user)
        message =  "====================================\n"
        message += "管理方操作 - 金額扣除\n"
        message += "====================================\n"
        message += f"發放人： {interaction.user.mention}\n"   
        message += f"金　額： {amount} 元\n"
        message += f"備　註： {note} \n" if note is not None else ""
        message += f"餘　額： {FromUser['balance']} 元\n"
        message += f"-# （若有疑慮，請操作客服單取向管理員聯繫）"
        await UserService.sendMessage(self.bot, interaction.guild.id, FromUser['uuid'], message)
        await interaction.response.send_message(embed=embed)

    # 上架任務
    @app_commands.command(name="上架任務", description="上架任務")
    @RoleService.checkBanned(False)
    @RoleService.checkManager(True)
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
                topicId = TopicServiceObject.create({'description': description, 'reward': reward, 'note': note})

                print(f"上架任務 - {interaction.user.name} - {description} - {reward} - {note}")
                embed = discord.Embed(title="任務上架成功", description="", color=Colour.gold())
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
                embed.description = f"# 任務快訊\n\n"
                embed.description += f"{interaction.user.mention} 上架了一則新簽到任務！\n"
                embed.description += f"-# 究竟誰會是第一位受害者呢？\n\n"
                embed.add_field(name="任務 ID", value=topicId, inline=False)
                embed.add_field(name="任務內容", value=description, inline=False)
                embed.add_field(name="任務獎勵", value='無' if reward is None else str(reward) + ' 元', inline=False)
                embed.add_field(name="任務備註", value="無" if note is None else note, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=False)
                await interaction.followup.send(f"{interaction.user.mention} 任務上架成功！", ephemeral=True)

        # # Modal
        await interaction.response.send_modal(TopicModal())

    # 任務清單
    @app_commands.command(name="任務清單", description="查看的任務有哪些")
    @RoleService.checkBanned(False)
    @RoleService.checkManager(True)
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
    @RoleService.checkBanned(False)
    @RoleService.checkManager(True)
    async def deleteTopic(self, interaction: discord.Interaction, topic_id: int):
        class ConfirmButton(discord.ui.Button):
            def __init__(self, *args, **kwargs):
                self.topic_id = kwargs.pop('topic_id')
                super().__init__(*args, **kwargs)

            async def callback(self, interaction: discord.Interaction):
                TopicServiceObject = TopicService()
                Topic = TopicServiceObject.findById(self.topic_id)
                if (Topic is None or Topic['deleted_at'] is not None):
                    await interaction.response.edit_message(content=f"{interaction.user.mention} 您查詢的任務不存在！", view=None)
                    return

                # 確認下架
                TopicServiceObject = TopicService()
                TopicServiceObject.delete([Topic['id']])

                self.disabled = True
                await interaction.response.edit_message(content=f"{interaction.user.mention} 已為您下架指定的任務～", view=self.view)

                embed = discord.Embed(title="管理方操作", description="任務下架", color=Colour.gold())
                embed.add_field(name="任務 ID", value=self.topic_id, inline=False)
                embed.add_field(name="任務內容", value=f"{Topic['description']}", inline=False)
                embed.add_field(name="任務獎勵", value=f"{Topic['reward']} 元" if Topic['reward'] is not None else "無", inline=False)
                embed.add_field(name="任務備注", value=Topic['note'] if Topic['note'] is not None else "無", inline=False)
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
                embed.set_footer(text=f"由 {interaction.user.display_name} 操作")
                await interaction.followup.send(embed=embed)
                return

        TopicServiceObject = TopicService()
        if (topic_id is None):
            await interaction.response.send_message(content=f"{interaction.user.mention} 您沒有選擇任何商品！", ephemeral=True)
            return
    
        Topic = TopicServiceObject.findById(topic_id)
        if (Topic is None or Topic['deleted_at'] is not None):
            await interaction.response.send_message(content=f"{interaction.user.mention} 您查詢的任務不存在！")
            return
        
        embed = discord.Embed(title="任務下架確認", description="")
        embed.description = f"{interaction.user.mention} 您好！這是您查詢的任務\n\n"
        embed.description += "-# **使用說明**\n"
        embed.description += "-# 若確定要下架這個任務，\n-# 請點選「確認下架」按鈕。\n\n\n"
        embed.add_field(name="任務 ID", value=topic_id, inline=False)
        embed.add_field(name="任務內容", value=f"{Topic['description']}", inline=False)
        embed.add_field(name="任務獎勵", value=f"{Topic['reward']} 元" if Topic['reward'] is not None else "無", inline=False)
        embed.add_field(name="任務備注", value=Topic['note'] if not None else "無", inline=False)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

        View = discord.ui.View(timeout=None)
        View.add_item(ConfirmButton(label="確認下架", style=discord.ButtonStyle.red, disabled=False, row=1, topic_id=topic_id))
        await interaction.response.send_message(embed=embed, view=View, ephemeral=True)

    # 強制下架商品
    @app_commands.command(name="強制下架商品", description="強制下架指定的商品")
    @app_commands.describe(merchandise_id="要下架的商品 ID，請透過「/shop 查看商品」指令查看", note="下架的理由或備註 - 若沒有則不填")
    @RoleService.checkBanned(False)
    @RoleService.checkManager(True)
    async def forceMerchandiseUnavailable(self, interaction: discord.Interaction, merchandise_id: int, note: str = None):
        class ConfirmButton(discord.ui.Button):
            def __init__(self, *args, **kwargs):
                self.merchandise_id = kwargs.pop('merchandise_id')
                self.note = kwargs.pop('note', None)
                super().__init__(*args, **kwargs)

            async def callback(self, interaction: discord.Interaction):
                Merchandise = MerchandiseServiceObject.findById(self.merchandise_id)
                if (Merchandise is None or Merchandise['deleted_at'] is not None):
                    await interaction.response.edit_message(content=f"{interaction.user.mention} 您查詢的商品不存在！", view=None)
                    return
                elif (Merchandise['system_type'] == MerchandiseSystemType.SYSTEM_CHECK_IN_REFRESH.value):
                    await interaction.response.edit_message(content=f"{interaction.user.mention} 任務刷新卷無法被下架！", view=None)
                    return

                # 確認下架
                UserServiceObject = UserService()
                User = UserServiceObject.firstOrCreate(interaction.user)
                MerchandiseServiceObject.delete(ids=[Merchandise['id']], user_id=User['id'])
                self.disabled = True
                await interaction.response.edit_message(content=f"{interaction.user.mention} 已為您下架指定的商品～", view=self.view)

                embed = discord.Embed(title="管理方操作", description="強制商品下架", color=Colour.gold())
                embed.add_field(name="商品 ID", value=merchandise_id, inline=False)
                embed.add_field(name="商品名稱", value=f"{Merchandise['name']}", inline=False)
                embed.add_field(name="商品描述", value=Merchandise['description'] if Merchandise['description'] is not None else "無", inline=False)
                embed.add_field(name="商品價格", value=f"{Merchandise['price']} 元", inline=False)
                embed.add_field(name="商品擁有者", value=f"<@{Merchandise['uuid']}>" if Merchandise['uuid'] is not None else "系統", inline=False)
                embed.add_field(name="下架備註", value=self.note if self.note is not None else "無", inline=False)
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
                embed.set_footer(text=f"由 {interaction.user.display_name} 操作")
                await interaction.followup.send(embed=embed)

                message =  "====================================\n"
                message += "管理方操作 - 強制商品下架\n"
                message += "====================================\n"
                message += f"管理員： {interaction.user.mention}\n"   
                message += f"擁有者： <@{Merchandise['uuid']}>\n"
                message += f"商品 ID： {merchandise_id}\n"
                message += f"商品名稱： {Merchandise['name']}\n"
                message += f"商品描述： "
                message += f"\n{Merchandise['description']}\n" if Merchandise['description'] is not None else '無\n'
                message += f"商品價格： {Merchandise['price']} 元\n"
                message += f"商品擁有者： <@{Merchandise['uuid']}>\n"
                message += f"下架備註： {self.note} \n" if self.note is not None else ''
                message += f"商品狀態： 已下架\n"
                message += f"-# （若有疑慮，請操作客服單取向管理員聯繫）"
                await UserService.sendMessage(interaction.client, interaction.guild.id, Merchandise['uuid'], message)
                return

        MerchandiseServiceObject = MerchandiseService()
        if (merchandise_id is None):
            await interaction.response.send_message(content=f"{interaction.user.mention} 您沒有選擇任何商品！", ephemeral=True)
            return
    
        Merchandise = MerchandiseServiceObject.findById(merchandise_id)
        if (Merchandise is None or Merchandise['deleted_at'] is not None):
            await interaction.response.send_message(content=f"{interaction.user.mention} 您查詢的商品不存在！", ephemeral=True)
            return
        
        embed = discord.Embed(title="商品下架確認", description="")
        embed.description = f"{interaction.user.mention} 您好！這是您查詢的商品\n\n"
        embed.description += "-# **使用說明**\n"
        embed.description += "-# 若確定要下架這個商品，\n-# 請點選「確認下架」按鈕。\n\n\n"
        embed.add_field(name="商品 ID", value=merchandise_id, inline=False)
        embed.add_field(name="商品名稱", value=f"{Merchandise['name']}", inline=False)
        embed.add_field(name="商品描述", value=Merchandise['description'] if Merchandise['description'] is not None else "無", inline=False)
        embed.add_field(name="商品價格", value=f"{Merchandise['price']} 元", inline=False)
        embed.add_field(name="商品擁有者", value=f"<@{Merchandise['uuid']}>" if Merchandise['uuid'] is not None else "系統", inline=False)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

        View = discord.ui.View(timeout=None)
        View.add_item(ConfirmButton(label="確認下架", style=discord.ButtonStyle.red, disabled=False, row=1, merchandise_id=merchandise_id, note=note))
        await interaction.response.send_message(embed=embed, view=View, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Manager(bot))
