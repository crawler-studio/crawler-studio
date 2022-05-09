from django.test import TestCase

# Create your tests here.
from apscheduler.schedulers.blocking import BlockingScheduler
import time


# 定时的任务，打印当前的时间
def test():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


scheduler = BlockingScheduler()
# 时间间隔5秒
scheduler.add_job(test, trigger='interval', seconds=5, id='test')
scheduler.start()
