from django.db import models
# Create your models here.


class SpiderStats(models.Model):

    id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=50)
    project = models.CharField(max_length=255)
    spider = models.CharField(max_length=255)
    job_id = models.CharField(max_length=50)
    run_type = models.CharField(max_length=50, verbose_name='interval or crontab')
    last_run = models.DateTimeField()
    trigger = models.CharField(max_length=50)
    record_time = models.DateTimeField(auto_now=True, verbose_name='当前时间')
    log_debug_count = models.BigIntegerField(default=0)
    log_info_count = models.BigIntegerField(default=0)
    log_warn_count = models.IntegerField(default=0)
    log_error_count = models.IntegerField(default=0)
    log_critical_count = models.IntegerField(default=0)
    log_error_rate = models.FloatField(verbose_name='日志错误率')
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField(null=True, default=None)
    finish_reason = models.CharField(max_length=255, verbose_name='爬虫关闭原因', default='', null=True)
    elapsed_time = models.CharField(max_length=255, null=True, default='')
    stats = models.TextField(verbose_name='统计数据')
    state = models.SmallIntegerField(verbose_name='1：正在运行， 0：已完成')
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)


class DailyErrLogRate(models.Model):
    """
    每天生成一条记录
    """
    id = models.AutoField(primary_key=True)
    job_id = models.CharField(max_length=50, db_index=True)
    log_total_count = models.IntegerField()
    log_error_count = models.IntegerField()
    log_error_rate = models.FloatField(verbose_name='一天范围日志错误率')
    log_date = models.DateField()


class HourlyErrLogRate(models.Model):
    """
    每小时生成一条记录
    """
    id = models.AutoField(primary_key=True)
    job_id = models.CharField(max_length=50, db_index=True)
    log_total_count = models.IntegerField()
    log_error_count = models.IntegerField()
    log_error_rate = models.FloatField(verbose_name='一小时范围日志错误率')
    log_date = models.DateField()
    log_hour = models.IntegerField(verbose_name='0-23 represent 24 hours')


class ErrorLog(models.Model):
    """
    专门记录error和critical级别的log
    """
    id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=50)
    project = models.CharField(max_length=255)
    spider = models.CharField(max_length=255)
    job_id = models.CharField(max_length=50)
    content = models.TextField()
    level = models.CharField(max_length=20)
    log_time = models.DateTimeField()
    module = models.CharField(max_length=1000)
    lineno = models.IntegerField()
    exc_info = models.TextField(null=True, default=None)
    func_name = models.CharField(max_length=255, default=None)
