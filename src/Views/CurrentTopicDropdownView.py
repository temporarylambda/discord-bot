import os
import discord
from Services.UserService import UserService
from Services.TopicService import TopicService

class CurrentTopicDropdown(discord.ui.Select):
    def __init__(self, dataset: list):
        options = [];
        for data in dataset:
            description = [];
            if (data['reward'] and str(data['reward']).isdigit() and int(data['reward']) > 0):
                description.append(f"獎勵 {data['reward']} 元")
            
            if (data['note'] is not None):
                description.append(f"{data['note']}")

            description = " | ".join(description)
            options.append(discord.SelectOption(label=data['description'], description=description, value=str(data['id'])))

        # 設定 max_values 為 os.getenv("RULE_CHECK_IN_MAX_TIMES") 與 options 長度的較小值
        max_values = min(int(os.getenv("RULE_CHECK_IN_MAX_TIMES", 1)), len(options))

        super().__init__(
            placeholder="選擇一個選項",
            min_values=1,
            max_values=max_values,
            options=options
        )

    # 不做任何事情，直接回傳
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class CurrentTopicDropdownView(discord.ui.View):
    def __init__(self, dataset: list):
        super().__init__()
        self.dropdown = CurrentTopicDropdown(dataset)
        self.add_item(self.dropdown)  # 將下拉選單添加到 View

    @discord.ui.button(label="確認回報", style=discord.ButtonStyle.green, disabled=False, row=1)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (len(self.dropdown.values) == 0):
            await interaction.response.send_message(f"{interaction.user.mention} 您沒有選擇任何任務！", ephemeral=True)
            return

        for value in self.dropdown.values:
            # 從 options 中找到對應的 label
            selected_label = next(
                (option.label for option in self.dropdown.options if option.value == value),
                None
            )
            # 你可以在這裡使用 selected_label
            print(f"使用者選擇了任務 ID: {value}, 對應的標籤是: {selected_label}")

        UserServiceObject = UserService()
        User = UserServiceObject.firstOrCreate(interaction.user)
        TopicServiceObject = TopicService()
        
        # 防範重複回報
        currentTopics = TopicServiceObject.getCurrentTopics(User['id'], self.dropdown.values) # 僅挑選出目前有選擇的任務，查詢他們是否目前正在進行中
        if len(currentTopics) == 0:
            await interaction.response.send_message(f"{interaction.user.mention} 您選擇的任務似乎都已經回報過囉！")
            return
        
        # 將取得的目前進行中任務跟使用者選擇的任務進行交集，作為實際回報的任務 
        selected_values = set(self.dropdown.values) & set([str(topic['id']) for topic in currentTopics])
        selected_values = list(selected_values)

        # 簽到
        TopicServiceObject.report(User['id'], selected_values)

        # 計算需要發放多少獎勵金
        rewardTopics = []
        for currentTopic in currentTopics:
            if str(currentTopic['id']) in selected_values:
                rewardTopics.append(currentTopic)
        reward = sum(item.get('reward', 0) for item in rewardTopics if item.get('reward') is not None)

        # TODO: 轉帳
        await interaction.response.send_message(f"{interaction.user.mention} 回報成功囉！\n您的獎勵也已經發放到您的帳戶了，共計 {reward} 元！")