from django.db import models

# Create your models here.


class EnvVariable(models.Model):
    """"""
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=50, default='dev', verbose_name='类型：local、dev、test、prod')
    db = models.CharField(max_length=255, verbose_name='数据库名称')
    user = models.CharField(max_length=255, verbose_name='数据库用户名')
    password = models.CharField(max_length=255, verbose_name='数据库密码')
    host = models.CharField(max_length=255, verbose_name='数据库地址')
    port = models.IntegerField(default=6379, verbose_name='数据库端口')
    comment = models.TextField(default='', verbose_name='备注')
