"""
@Description: 
@Usage: 
@Author: liuxianglong
"""
from django.core.management import BaseCommand
from crawler_studio.app_scrapyd.models import SpiderStartParams


class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        self.create_default_monitor_params()
        print('init finished')

    @staticmethod
    def create_default_monitor_params():
        SpiderStartParams.objects.get_or_create(
            project='__default',
            spider='__default',
            monitor_freq=300,
            errlog_rate_limit=0.01,
            memory_use_limit=300,
            enable_send_error_log=True,
            enable_monitor_rule=True,
        )

    def add_arguments(self, parser):
        pass
