from django.db import models

# Create your models here.


class DeployParams(models.Model):
    fabric_code = models.CharField(max_length=1024)
    fabric_host = models.CharField(max_length=1024)
    fabric_user = models.CharField(max_length=1024)
    fabric_ssh_key_path = models.CharField(max_length=1024)
    fabric_code_path = models.CharField(max_length=1024)
    deploy_scrapyd_addr = models.CharField(max_length=1024)
    deploy_mode = models.CharField(max_length=1024)
    state = models.SmallIntegerField()
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()

    class Meta:
        app_label = 'crawler_studio_be'
        verbose_name = '新闻表'
        db_table = 'deploy_params'
