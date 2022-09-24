"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/2/2 下午2:55
"""
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore())
scheduler.start()

