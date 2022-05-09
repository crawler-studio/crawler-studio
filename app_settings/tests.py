from django.test import TestCase

# Create your tests here.
import requests

headers = {'Content-Type': 'application/json'}


def post():
    body = {
        'addr': 'http://127.0.0.2:6800/'
    }
    resp = requests.post('http://127.0.0.1:8000/api/v1/settings/scrapydserver/', json=body, headers=headers)
    print(resp.json())


def delete():
    body = {
        'addr': 'http://127.0.0.3:6800/'
    }
    resp = requests.delete('http://127.0.0.1:8000/api/v1/settings/scrapydserver/', json=body, headers=headers)
    print(resp.json())


def put():
    body = {
        'addr': 'http://10.0.4.150:6800',
        'is_default': 1
    }
    resp = requests.put('http://127.0.0.1:8000/api/v1/settings/scrapydserver/', json=body, headers=headers)
    print(resp.json())


if __name__ == '__main__':
    # post()
    # delete()
    put()