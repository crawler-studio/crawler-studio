from django.shortcuts import render

# Create your views here.
import datetime
from dateutil import parser as dfparser
import gitlab
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from crawler_studio.app_settings.models import ScrapydServer, LogServer
from django.forms.models import model_to_dict


class ScrapydServerAddr(View):
    """
    http://localhost:8000/api/v1/settings/scrapydserver/
    """

    def get(self, request):
        data = [model_to_dict(_) for _ in ScrapydServer.objects.all()]
        return JsonResponse(data, safe=False)

    def post(self, request):
        data = eval(request.body.decode())
        obj, created = ScrapydServer.objects.get_or_create(addr=data['addr'], defaults=data)
        if created:
            return JsonResponse({'code': 0, 'msg': '添加scrapyd服务器成功'})
        else:
            return JsonResponse({'code': 0, 'msg': '服务器已存在'})

    def delete(self, request):
        data = eval(request.body.decode())
        result = ScrapydServer.objects.filter(addr=data['addr']).delete()
        if result[0] == 1:
            return JsonResponse({'code': 0, 'msg': '删除成功'})
        else:
            return JsonResponse({'code': -1, 'msg': f'数据库中没有服务器 {data["addr"]}'})

    def put(self, request):
        data = eval(request.body.decode())
        ScrapydServer.objects.filter(is_default=1).update(is_default=0)
        ScrapydServer.objects.filter(addr=data['addr']).update(is_default=1)
        return JsonResponse({'code': 0})


class LogServerAddr(View):
    """
    http://localhost:8000/api/v1/settings/logserver/
    """

    def get(self, request):
        data = [model_to_dict(_) for _ in LogServer.objects.all()]
        return JsonResponse(data, safe=False)

    def post(self, request):
        data = eval(request.body.decode())
        obj, created = LogServer.objects.get_or_create(addr=data['addr'], defaults=data)
        if created:
            return JsonResponse({'code': 0, 'msg': '添加日志服务器成功'})
        else:
            return JsonResponse({'code': 0, 'msg': '服务器已存在'})

    def delete(self, request):
        data = eval(request.body.decode())
        result = LogServer.objects.filter(addr=data['addr']).delete()
        if result[0] == 1:
            return JsonResponse({'code': 0, 'msg': '删除成功'})
        else:
            return JsonResponse({'code': -1, 'msg': f'数据库中没有服务器 {data["addr"]}'})

    def put(self, request):
        data = eval(request.body.decode())
        LogServer.objects.filter(is_default=1).update(is_default=0)
        LogServer.objects.filter(addr=data['addr']).update(is_default=1)
        return JsonResponse({'code': 0})
