from django.db import models
from django_apscheduler.models import DjangoJob, DjangoJobExecution
# Create your models here.


class MonitorRecipients(models.Model):
    id = models.AutoField(primary_key=True)
    method = models.CharField(max_length=50, verbose_name="通知工具，邮件或者钉钉")
    rev_addr = models.CharField(max_length=255, unique=True, verbose_name="地址")
    rev_name = models.CharField(null=True, max_length=100, unique=True, verbose_name="名称")
    is_default = models.SmallIntegerField(default=0, verbose_name='0: 不是默认， 1：默认收件人')
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)


class MonitorRules(models.Model):
    id = models.AutoField(primary_key=True)
    timer_task = models.OneToOneField(DjangoJob, null=True, on_delete=models.CASCADE)
    spider_host = models.CharField(max_length=50, verbose_name='爬虫所在主机')
    spider_project = models.CharField(null=True, max_length=100, verbose_name='爬虫项目')
    spider_name = models.CharField(null=True, max_length=100, verbose_name='爬虫名称')
    spider_job_id = models.CharField(null=True, max_length=100, db_index=True)
    start_params = models.CharField(null=True, max_length=1000, verbose_name='启动参数')
    # monitor_type = models.CharField(max_length=50, null=True, verbose_name='预警方式，1:日志存活时间，2:日志错误率, 3:日志错误数量')
    monitor_freq = models.IntegerField(verbose_name='监控频率，秒为单位', default=1800)
    log_alive_limit = models.IntegerField(default=80, verbose_name='日志存活时间上限, 默认80sec')
    errlog_rate_limit = models.FloatField(default=0.005, verbose_name='1小时日志错误率上限，默认0.5%')
    memory_use_limit = models.IntegerField(default=500, verbose_name='占用最大内存，默认500MB')
    recipients = models.ManyToManyField(MonitorRecipients, verbose_name='收件人')
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)
