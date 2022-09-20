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
        return Response(ser.data)

    def post(self, request):
        data = eval(request.body.decode())
        obj, created = ScrapydServer.objects.get_or_create(addr=data['addr'], defaults=data)
        if created:
            return Response({'code': 0, 'msg': '添加scrapyd服务器成功'})
        else:
            return Response({'code': 0, 'msg': '服务器已存在'})

    def delete(self, request):
        data = eval(request.body.decode())
        result = ScrapydServer.objects.filter(addr=data['addr']).delete()
        if result[0] == 1:
            return Response({'code': 0, 'msg': '删除成功'})
        else:
            return Response({'code': -1, 'msg': f'数据库中没有服务器 {data["addr"]}'})

    def put(self, request):
        data = eval(request.body.decode())
        ScrapydServer.objects.filter(is_default=1).update(is_default=0)
        ScrapydServer.objects.filter(addr=data['addr']).update(is_default=1)
        return Response({'code': 0})
