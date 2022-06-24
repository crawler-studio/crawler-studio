from django.db import models
# Create your models here.


class SpiderStats(models.Model):
    """爬虫运行状态表"""
    id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=50)
    project = models.CharField(max_length=255)
    spider = models.CharField(max_length=255)
    job_id = models.CharField(max_length=50, db_index=True)
    run_type = models.CharField(max_length=50, verbose_name='interval or crontab')
    last_run = models.DateTimeField()
    trigger = models.CharField(max_length=50)
    record_time = models.DateTimeField(auto_now=True, verbose_name='当前时间')
    log_debug_count = models.BigIntegerField(default=0)
    log_info_count = models.BigIntegerField(default=0)
    log_warn_count = models.IntegerField(default=0)
    log_error_count = models.IntegerField(default=0)
    log_critical_count = models.IntegerField(default=0)
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField(null=True, default=None)
    finish_reason = models.CharField(max_length=255, verbose_name='爬虫关闭原因', default='', null=True)
    elapsed_time = models.CharField(max_length=255, null=True, default='')
    stats = models.TextField(verbose_name='统计数据')
    state = models.SmallIntegerField(verbose_name='1：正在运行， 0：已完成')
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)
