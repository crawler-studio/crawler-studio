from django.db import models
from django_apscheduler.models import DjangoJob, DjangoJobExecution
# Create your models here.


class MonitorRecipients(models.Model):
    id = models.AutoField(primary_key=True)
    method = models.CharField(max_length=50, verbose_name="通知工具，邮件或者钉钉")
    rev_addr = models.CharField(max_length=255, unique=True, verbose_name="地址")
    rev_name = models.CharField(null=True, max_length=100, unique=True, verbose_name="名称")
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)


class MonitorRules(models.Model):
    id = models.AutoField(primary_key=True)
    # timer_task = models.OneToOneField(DjangoJob, null=True, on_delete=models.CASCADE)
    spider_host = models.CharField(max_length=50, verbose_name='爬虫所在主机')
    spider_project = models.CharField(null=True, max_length=100, verbose_name='爬虫项目')
    spider_name = models.CharField(null=True, max_length=100, verbose_name='爬虫名称')
    spider_job_id = models.CharField(null=True, max_length=100)
    # monitor_type = models.CharField(max_length=50, null=True, verbose_name='预警方式，1:日志存活时间，2:日志错误率, 3:日志错误数量')
    # monitor_freq = models.IntegerField(verbose_name='监控频率，秒为单位', default=1800)
    # threshold = models.IntegerField(null=True, verbose_name='报警阈值')
    recipients = models.ManyToManyField(MonitorRecipients, verbose_name='收件人')
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)
