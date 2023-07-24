"""
@Description: 获取用户的token
@Usage: 
@Author: liuxianglong
"""
from rest_framework.test import APIClient
from django.core.management import BaseCommand


class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.client = APIClient()

    def handle(self, *args, **options):
        body = {
            "username": options['username'],
            "password": options['password']
        }
        try:
            resp = self.client.post('/api/v1/api-token-auth/', body, format='json')
            print(resp.json()['token'])
        except Exception as e:
            print(e)

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', action='store', dest='username', default='')
        parser.add_argument('-p', '--password', action='store', dest='password', default='')
