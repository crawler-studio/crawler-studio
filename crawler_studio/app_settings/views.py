from django.shortcuts import render

# Create your views here.
from .ser import ScrapydServerSer
from .models import ScrapydServer
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.views import APIView


class ScrapydServerAddr(APIView):
    """
    http://localhost:8000/api/v1/settings/scrapydserver/
    """

    def get(self, request):
        data = ScrapydServer.objects.all()
        ser = ScrapydServerSer(data, many=True)
        res = {
            'code': 200,
            'data': {
                'data': ser.data
            },
            'message': 'ok'
        }
        return Response(res)

    def post(self, request):
        data = eval(request.body.decode())
        obj, created = ScrapydServer.objects.get_or_create(addr=data['addr'], defaults=data)
        if created:
            res = {
                'code': 200,
                'data': None,
                'message': '添加scrapyd服务器成功'
            }
            return Response(res)
        else:
            res = {
                'code': 300,
                'data': None,
                'message': '服务器已存在'
            }
            return Response(res)

    def delete(self, request):
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

    def put(self, request):
        data = eval(request.body.decode())
        ScrapydServer.objects.filter(is_default=1).update(is_default=0)
        ScrapydServer.objects.filter(addr=data['addr']).update(is_default=1)
        res = {
            'code': 200,
            'data': None,
            'message': '修改默认服务器成功'
        }
        return Response(res)
