import os
import signal
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BotReloader(FileSystemEventHandler):
    def __init__(self, bot_process):
        self.bot_process = bot_process

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"🔄 偵測到 {event.src_path} 變更，正在重新啟動 Bot...")
            self.restart_bot()

    def restart_bot(self):
        self.bot_process.terminate()  # 結束舊的 Bot
        self.bot_process.wait()
        self.bot_process = subprocess.Popen(["python", "bot.py"])  # 啟動新的 Bot

if __name__ == "__main__":
    bot_process = subprocess.Popen(["python", "bot.py"])
    event_handler = BotReloader(bot_process)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)  # 監聽整個資料夾
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        bot_process.terminate()
        observer.stop()
    observer.join()
