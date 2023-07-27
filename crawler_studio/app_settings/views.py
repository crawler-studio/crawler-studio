from django.shortcuts import render

# Create your views here.
from .ser import *
from .models import *
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.views import APIView


class ScrapydServerAddr(APIView):
    """
    http://localhost:8000/api/v1/settings/scrapydserver/
    """

    def get(self, request, **kwargs):
        data = ScrapydServer.objects.all().order_by('alias')
        ser = ScrapydServerSer(data, many=True)
        res = {
            'code': 200,
            'data': {
                'data': ser.data
            },
            'message': 'ok'
        }
        return Response(res)

    def post(self, request, **kwargs):
        addr = request.data['addr']

        existed = ScrapydServer.objects.filter(addr=addr).first()
        if existed:
            res = {
                'code': 300,
                'data': None,
                'message': '服务器已存在'
            }
            return Response(res)

        server = ScrapydServerSer(instance=existed, data=request.data)
        if server.is_valid():
            server.save()
            res = {
                'code': 200,
                'data': None,
                'message': '添加scrapyd服务器成功'
            }
            return Response(res)
        else:
            server.save()
            res = {
                'code': 400,
                'data': None,
                'message': server.errors
            }
            return Response(res)

    def delete(self, request, **kwargs):
        data = eval(request.body.decode())
        result = ScrapydServer.objects.filter(addr=data['addr']).delete()
        if result[0] == 1:
            res = {
                'code': 200,
                'data': None,
                'message': '删除成功'
            }
            return Response(res)
        else:
            res = {
                'code': 400,
                'data': None,
                'message': f'数据库中没有服务器 {data["addr"]}'
            }
            return Response(res)

    def put(self, request, **kwargs):
        data = eval(request.body.decode())
        ScrapydServer.objects.filter(is_default=1).update(is_default=0)
        ScrapydServer.objects.filter(addr=data['addr']).update(is_default=1)
        res = {
            'code': 200,
            'data': None,
            'message': '修改默认服务器成功'
        }
        return Response(res)


class MailSenderCRUD(APIView):

    def get(self, request, **kwargs):
        data = MailSender.objects.first()
        ser = MailSenderSer(data)
        res = {
            'code': 200,
            'data': {
                'data': ser.data
            },
            'message': 'ok'
        }
        return Response(res)

    def post(self, request, **kwargs):
        print(request.data)
        existed = MailSender.objects.first()
        sender = MailSenderSer(instance=existed, data=request.data)
        if sender.is_valid():
            sender.save()
            res = {
                'code': 200,
                'data': None,
                'message': '添加成功' if not existed else '修改成功'
            }
            return Response(res)
        else:
            sender.save()
            res = {
                'code': 400,
                'data': None,
                'message': sender.errors
            }
            return Response(res)
