import os
from Repositories.TopicRepository import TopicRepository
from Repositories.DailyCheckInTopicRepository import DailyCheckInTopicRepository

class TopicService:
    def __init__(self):
        self.DailyCheckInTopicRepository = DailyCheckInTopicRepository();
        self.TopicRepository = TopicRepository();
        self.limitation = os.getenv("RULE_CHECK_IN_MAX_TIMES");
    
    # 取得目前尚未結束的報到題目
    def getCurrentTopics(self, discord_id):
        return self.DailyCheckInTopicRepository.getCurrentTopics(discord_id);
    
    # 檢查目前待完成的簽到題目是否已經滿了
    def isUnavailable(self, discord_id):
        limitation = os.getenv("RULE_CHECK_IN_MAX_TIMES");
        return len(self.DailyCheckInTopicRepository.getCurrentTopics(discord_id)) >= int(self.limitation);

    # 檢查今天已經領取的報到題目是否已經滿了
    def isTodayTaken(self, discord_id):
        limitation = os.getenv("RULE_CHECK_IN_MAX_TIMES");
        return len(self.DailyCheckInTopicRepository.getTodayTakenTopics(discord_id)) >= int(self.limitation);

    # 隨機取得一條題目，並將該題目登記為待執行
    def take(self, discord_id):
        topic = self.TopicRepository.random();
        self.DailyCheckInTopicRepository.register(discord_id, topic[0]);
        return topic

    # TODO: 回報一道題目已經完成
    def report(self, discord_id, amount, note=None):
        return;

    # TODO: 跳過一道題目
    def skip(self, discord_id, amount, note=None):
        return;