from django.http import HttpResponse, JsonResponse
from app_docs.models import Docs, DocsType


def create(request):
    """新增文档数据"""
    item = {
        'project': request.GET['project'],
        'title': request.GET['title'],
        'author': request.GET['author'],
        'created_at': request.GET['created_at'],
        'doc_type': request.GET['doc_type']
    }
    obj, created = Docs.objects.get_or_create(link=request.GET['link'], display=1, defaults=item)
    if created:
        return JsonResponse({'code': 0, 'msg': '创建成功'})
    else:
        return JsonResponse({'code': -1, 'msg': '文档链接已经存在'})


def delete(request):
    """
    删除文档数据
    http://localhost:8000/api/v1/docs/delete?id=12
    """
    docid = request.GET['id']
    res = Docs.objects.filter(id=docid).first()
    if res:
        res.display = 0
        res.save()
        return JsonResponse({'code': 0, 'msg': '删除成功'})
    else:
        return JsonResponse({'code': -1, 'msg': '元素不存在'})


def query(request):
    """
    获取所有文档记录
    http://127.0.0.1:8000/api/v1/docs/get/
    """
    data = list(Docs.objects.filter(display=1).values())
    return JsonResponse(data, safe=False)


def update(request):
    """更新文档数据"""
    item = {
        'project': request.GET['project'],
        'title': request.GET['title'],
        'author': request.GET['author'],
        'created_at': request.GET['created_at'],
        'link': request.GET['link'],
        'doc_type': request.GET['doc_type']
    }
    if Docs.objects.filter(link=item['link']).exclude(id=request.GET['id']):
        return JsonResponse({'code': -1, 'msg': '文档链接已存在'})
    else:
        Docs.objects.filter(id=request.GET['id']).update(**item)
        return JsonResponse({'code': 0, 'msg': '更新文档成功'})


def get_max_id(request):
    """
    获取所有文档当前最大ID
    http://127.0.0.1:8000/api/v1/docs/get_max_id/
    """
    if Docs.objects.count() > 0:
        return JsonResponse({'max_id': Docs.objects.latest('id').id})
    else:
        return JsonResponse({'max_id': 0})


def get_doc_type(request):
    """
    获取所有文档类型
    http://127.0.0.1:8000/api/v1/docs/get_doc_type/
    """
    types = list(DocsType.objects.all().values('doc_type'))
    types = [_['doc_type'] for _ in types]
    return JsonResponse(types, safe=False)
