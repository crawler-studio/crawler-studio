"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/9/23 上午1:06
"""
from django.db import models


class DailyErrLogRate(models.Model):
    """
    每天生成一条记录
    """
    id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=50)
    project = models.CharField(max_length=255)
    spider = models.CharField(max_length=255)
    job_id = models.CharField(max_length=50, db_index=True)
    record_time = models.DateTimeField(db_index=True)
    log_total_count = models.IntegerField()
    log_error_count = models.IntegerField()
    log_error_rate = models.FloatField(verbose_name='一天范围日志错误率')
    log_date = models.DateField()
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)


class HourlyErrLogRate(models.Model):
    """
    每小时生成一条记录
    """
    id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=50)
    project = models.CharField(max_length=255)
    spider = models.CharField(max_length=255)
    job_id = models.CharField(max_length=50, db_index=True)
    record_time = models.DateTimeField(db_index=True)
    log_total_count = models.IntegerField()
    log_error_count = models.IntegerField()
    log_error_rate = models.FloatField(verbose_name='一小时范围日志错误率')
    log_date = models.DateField()
    log_hour = models.IntegerField(verbose_name='0-23 represent 24 hours')
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)


class ErrorLog(models.Model):
    """
    专门记录error和critical级别的log
    """
    id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=50)
    project = models.CharField(max_length=255)
    spider = models.CharField(max_length=255)
    job_id = models.CharField(max_length=50, db_index=True)
    record_time = models.DateTimeField(db_index=True)
    content = models.TextField()
    level = models.CharField(max_length=20)
    log_time = models.DateTimeField(db_index=True)
    module = models.CharField(max_length=1000)
    lineno = models.IntegerField()
    exc_info = models.TextField(null=True, default=None)
    func_name = models.CharField(max_length=255, default=None)
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)
