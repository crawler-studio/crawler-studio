# Generated by Django 3.2.15 on 2022-11-14 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_scrapyd', '0005_auto_20220923_0112'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpiderStartParams',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('project', models.CharField(max_length=255)),
                ('spider', models.CharField(max_length=255)),
                ('run_type', models.CharField(max_length=50, verbose_name='interval or crontab')),
                ('trigger', models.CharField(max_length=50)),
                ('monitor_freq', models.IntegerField()),
                ('errlog_rate_limit', models.FloatField()),
                ('memory_use_limit', models.IntegerField(verbose_name='内存使用上限')),
                ('enable_send_error_log', models.BooleanField(verbose_name='是否发送错误日志内容到服务器')),
                ('enable_monitor_rule', models.BooleanField(verbose_name='是否开启爬虫监控')),
                ('monitor_recipients', models.CharField(max_length=255)),
                ('params', models.TextField(null=True, verbose_name='其他启动参数')),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]