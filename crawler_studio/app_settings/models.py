from django.db import models

# Create your models here.


class ScrapydServer(models.Model):
    id = models.AutoField(primary_key=True)
    addr = models.CharField(unique=True, max_length=50)
    alias = models.CharField(max_length=100, default='')
    is_default = models.SmallIntegerField(default=0)
    create_time = models.DateTimeField(auto_now=True, db_index=True)
    update_time = models.DateTimeField(auto_now_add=True, db_index=True)


class LogServer(models.Model):
    id = models.AutoField(primary_key=True)
    addr = models.CharField(unique=True, max_length=50)
    alias = models.CharField(max_length=100, default='')
    is_default = models.SmallIntegerField(default=0)
    create_time = models.DateTimeField(auto_now=True, db_index=True)
    update_time = models.DateTimeField(auto_now_add=True, db_index=True)