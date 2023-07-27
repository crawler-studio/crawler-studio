from django.db import models
# Create your models here.


class SpiderStats(models.Model):
    """爬虫运行状态表"""
    id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=50)
    project = models.CharField(max_length=255)
    spider = models.CharField(max_length=255)
    job_id = models.CharField(max_length=50, db_index=True)
    record_time = models.DateTimeField(auto_now=True, verbose_name='当前时间')
    log_debug_count = models.BigIntegerField(default=0)
    log_info_count = models.BigIntegerField(default=0)
    log_warn_count = models.IntegerField(default=0)
    log_error_count = models.IntegerField(default=0)
    log_critical_count = models.IntegerField(default=0)
    log_hourly_error_rate = models.FloatField(verbose_name='1小时日志错误率')
    memory_use = models.FloatField(null=True, verbose_name='占用最大的内存')
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField(null=True, default=None)
    finish_reason = models.CharField(max_length=255, verbose_name='爬虫关闭原因', default='', null=True)
    elapsed_time = models.CharField(max_length=255, null=True, default='')
    stats = models.TextField(verbose_name='统计数据')
    state = models.SmallIntegerField(verbose_name='1：正在运行， 0：已完成')
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)


class SpiderStartParams(models.Model):
    """爬虫启动参数表"""
    id = models.AutoField(primary_key=True)
    project = models.CharField(max_length=255)
    spider = models.CharField(max_length=255)
    run_type = models.CharField(max_length=50, verbose_name='interval or crontab')
    trigger = models.CharField(max_length=50)
    monitor_freq = models.IntegerField()
    errlog_rate_limit = models.FloatField()
    memory_use_limit = models.IntegerField(verbose_name='内存使用上限')
    enable_send_error_log = models.BooleanField(verbose_name='是否发送错误日志内容到服务器')
    enable_monitor_rule = models.BooleanField(verbose_name='是否开启爬虫监控')
    monitor_recipients = models.CharField(max_length=255)
    params = models.TextField(verbose_name='其他启动参数', null=True)
    description = models.CharField(max_length=2000, verbose_name='说明', null=True)
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)
