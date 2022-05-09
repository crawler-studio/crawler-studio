from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    email = models.EmailField(max_length=32)

    class Meta:
        app_label = 'crawler_studio_be'
        verbose_name = '账户表'
        db_table = 'user_info'
