import os
import discord
from Repositories.TopicRepository import TopicRepository
from Repositories.UserRepository import UserRepository
from Repositories.DailyCheckInTopicRepository import DailyCheckInTopicRepository
from Repositories.UserInventoryRepository import UserInventoryRepository

class TopicService:
    def __init__(self):
        self.DailyCheckInTopicRepository = DailyCheckInTopicRepository();
        self.TopicRepository = TopicRepository();
        self.UserInventoryRepository = UserInventoryRepository();
        self.limitation = os.getenv("RULE_CHECK_IN_MAX_TIMES");
    
    # 取得目前尚未結束的報到題目
    def getCurrentTopics(self, user_id, ids: list = []):
        return self.DailyCheckInTopicRepository.getCurrentTopics(user_id, ids);

    # 取得目前尚未結束的報到題目 - 下拉選單用
    def getCurrentTopicsDropdownOptions(self, user_id, ids: list = []):
        options = []
        DailyCheckInTopics = self.DailyCheckInTopicRepository.getCurrentTopics(user_id, ids)
        if (len(DailyCheckInTopics) > 0):
            for index, DailyCheckInTopic in enumerate(DailyCheckInTopics):
                description = '';
                if (DailyCheckInTopic['reward'] is not None):
                    description = f"獎勵 {DailyCheckInTopic['reward']} 元"
                if (DailyCheckInTopic['note'] is not None):
                    description += ' | ' if description != '' else ''
                    description += f"{DailyCheckInTopic['note']}"
                options.append(discord.SelectOption(label=DailyCheckInTopic['description'], description=description, value=str(DailyCheckInTopic['id'])))
        return options

    # 檢查目前待完成的簽到題目是否已經滿了
    def isUnavailable(self, user_id):
        limitation = os.getenv("RULE_CHECK_IN_MAX_TIMES");
        return len(self.DailyCheckInTopicRepository.getCurrentTopics(user_id)) >= int(self.limitation);

    # 檢查今天已經領取的報到題目是否已經滿了
    def isTodayTaken(self, user_id):
        return len(self.DailyCheckInTopicRepository.getTodayTakenTopics(user_id)) >= int(self.limitation);

    # 隨機取得一條題目，並將該題目登記為待執行
    def take(self, user_id):
        topic = self.TopicRepository.random();
        self.DailyCheckInTopicRepository.register(user_id, topic['id']);
        return topic

    # 回報一道題目已經完成
    def complete(self, user_id, daily_check_in_topic_ids: list):
        if len(daily_check_in_topic_ids) == 0:
            return;
        updatedRowsCount = self.DailyCheckInTopicRepository.complete(user_id, daily_check_in_topic_ids);
        
        # 更新最後簽到天數
        UserRepositoryObject = UserRepository();
        UserRepositoryObject.checkIn(user_id);
        return updatedRowsCount;

    def create(self, topic: dict):
        return self.TopicRepository.create(topic);

    def getAllPaginates(self, page: int = 1, page_size: int = 10):
        return self.TopicRepository.getAllPaginates(page, page_size);

    def delete(self, ids: list = []):
        return self.TopicRepository.delete(ids=ids);