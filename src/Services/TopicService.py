import os
from Repositories.TopicRepository import TopicRepository
from Repositories.UserRepository import UserRepository
from Repositories.DailyCheckInTopicRepository import DailyCheckInTopicRepository

class TopicService:
    def __init__(self):
        self.DailyCheckInTopicRepository = DailyCheckInTopicRepository();
        self.TopicRepository = TopicRepository();
        self.limitation = os.getenv("RULE_CHECK_IN_MAX_TIMES");
    
    # 取得目前尚未結束的報到題目
    def getCurrentTopics(self, user_id, ids: list = []):
        return self.DailyCheckInTopicRepository.getCurrentTopics(user_id, ids);
    
    # 檢查目前待完成的簽到題目是否已經滿了
    def isUnavailable(self, user_id):
        limitation = os.getenv("RULE_CHECK_IN_MAX_TIMES");
        return len(self.DailyCheckInTopicRepository.getCurrentTopics(user_id)) >= int(self.limitation);

    # 檢查今天已經領取的報到題目是否已經滿了
    def isTodayTaken(self, user_id):
        limitation = os.getenv("RULE_CHECK_IN_MAX_TIMES");
        return len(self.DailyCheckInTopicRepository.getTodayTakenTopics(user_id)) >= int(self.limitation);

    # 隨機取得一條題目，並將該題目登記為待執行
    def take(self, user_id):
        topic = self.TopicRepository.random();
        self.DailyCheckInTopicRepository.register(user_id, topic['id']);
        return topic

    # 回報一道題目已經完成
    def report(self, user_id, daily_check_in_topic_ids: list):
        if len(daily_check_in_topic_ids) == 0:
            return;
        updatedRowsCount = self.DailyCheckInTopicRepository.complete(user_id, daily_check_in_topic_ids);
        
        # 更新最後簽到天數
        UserRepositoryObject = UserRepository();
        UserRepositoryObject.checkIn(user_id);
        return updatedRowsCount;

    # TODO: 跳過一道題目
    def skip(self, user_id, amount, note=None):
        return;