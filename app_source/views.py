import logging
import json
import uuid
import tldextract
from urllib.parse import urlparse, urldefrag
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import Response
from django.forms.models import model_to_dict
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from utils.variable_rule_trans import to_snake_case_upper
from utils.timer_scheduler import scheduler
from app_source.models import Source2Timer
from app_schedule import worker
from app_source.serializers import *


class CategoryCRUD(APIView):
    """
    Method: GET
        type: parent
        desc: 根据父目录ID查询子节点，用于目录树的懒加载
        url: http://localhost:8000/api/v1/source/category/parent/?id=0
        return: {code: 0, data: [{}, {}, {}], msg: null}
        ----------------------
        type: category
        desc: 根据目录ID查询节点详情
        url: http://localhost:8000/api/v1/source/category/category/?id=10121
        return: {code: 0, data: {}, msg: null}
        ----------------------
        type: max_id
        desc: 查询当前目录结构中的最大目录ID，用于新建节点时的递增
        url: http://localhost:8000/api/v1/source/category/max_id/
        return:  {code: 0, data: 10332, msg: null}
        ----------------------
        type: full_tree
        desc: 查询目录树的所有节点，以树的形式返回
        url: http://localhost:8000/api/v1/source/category/full_tree/
        return: {code: 0, data: [{}, {}, {}], msg: null}


    Method: Post
        type: save
        desc: 新建或更新一个目录节点
        url: http://localhost:8000/api/v1/source/category/save/
        body:
        {
            'categoryId': 10321,
            'categoryName': '测试',
            'parentId': 0,
            'path': '测试',
            'level': 0,
            'fullPath': '/测试',
        }
        return:
        ----------------------
        type: delete
        desc: 删除一个目录节点
        url: http://localhost:8000/api/v1/source/category/delete/
        body:
        {
            'categoryId': 10321,
        }
    """

    def iter_tree(self, parent_id, result: list, cate_num: dict):
        """
        parent_id:
        result: 存储结果用
        cate_num: 目录下对应的源数量
        """
        data = Category.objects.filter(PARENT_ID=parent_id, IS_DELETE=0).all().values('CATEGORY_ID', 'CATEGORY_NAME')
        if not data:
            return

        for item in data:
            num = cate_num.get(item['CATEGORY_ID'], 0)
            subitem = {
                'id': item['CATEGORY_ID'],
                'label': f"{item['CATEGORY_NAME']}({num})",
                'name': item['CATEGORY_NAME'],
                'sourceNum': num,
                'children': []
            }
            result.append(subitem)
            self.iter_tree(item['CATEGORY_ID'], subitem['children'], cate_num)

    def iter_delete(self, category_id):
        Source2Category.objects.filter(CATEGORY_ID=category_id).delete()
        Category.objects.filter(CATEGORY_ID=category_id, IS_DELETE=0).update(IS_DELETE=1)
        for sub in Category.objects.filter(PARENT_ID=category_id, IS_DELETE=0).all():
            self.iter_delete(sub.CATEGORY_ID)

    def get(self, request, *args, **kwargs):
        ptype = kwargs['type']
        pid = request.GET.get('id')
        if ptype == 'parent' and pid:
            data = Category.objects.filter(PARENT_ID=pid, IS_DELETE=0).all()
            serializer = CategorySerializer(many=True, instance=data)
            return Response(serializer.data)
        elif ptype == 'category' and pid:
            cate = Category.objects.filter(CATEGORY_ID=pid, IS_DELETE=0).first()
            parent_node = Category.objects.filter(CATEGORY_ID=cate.PARENT_ID).first()
            cate_data = CategorySerializer(instance=cate).data
            cate_data.update({'PARENT_NAME': parent_node.CATEGORY_NAME if parent_node else '/'})
            sql = """
            select 1 as SOURCE_ID, count(*) as num FROM
            source_base b JOIN
            source_2_category c
            WHERE b.source_id = c.source_id AND b.IS_DELETE=0
            AND c.CATEGORY_ID={}
            """.format(pid)
            source_num = SourceBase.objects.raw(sql)
            source_num = source_num[0].num
            if cate:
                result = {
                    'code': 0,
                    'data': cate_data,
                    'source_num': source_num,
                    'msg': None
                }
                return Response(result)
            else:
                result = {
                    'code': 100,
                    'data': None,
                    'msg': f'节点不存在 {pid}'
                }
                return Response(result)
        elif ptype == 'max_id':
            r = Category.objects.all().aggregate(Max('CATEGORY_ID'))
            if r['CATEGORY_ID__max']:
                max_id = r['CATEGORY_ID__max']
            else:
                max_id = 10000
            result = {
                'code': 0,
                'data': max_id,
                'msg': None
            }
            return Response(result)
        elif ptype == 'full_tree':
            # 求目录下各个category的源数量
            sql = """
            select 1 as SOURCE_ID, c.CATEGORY_ID, count(*) as num FROM
            source_base b JOIN
            source_2_category c
            WHERE b.source_id = c.source_id AND b.IS_DELETE=0
            GROUP BY c.CATEGORY_ID ORDER BY num desc
            """
            cate_num = SourceBase.objects.raw(sql)
            cate_num = {_.CATEGORY_ID: _.num for _ in cate_num}
            # 迭代目录树
            data = list()
            self.iter_tree(0, data, cate_num)
            result = {
                'code': 0,
                'data': data,
                'msg': None,
            }
            return Response(result)
        else:
            return Response({'code': 999, 'msg': '参数问题'})

    def post(self, request, **kwargs):
        ptype = kwargs['type']
        if ptype == 'save':
            body = json.loads(request.body)
            item = {
                'CATEGORY_NAME': body['categoryName'],
                'PARENT_ID': body['parentId'],
                'PATH': body['path'],
                'LEVEL': body['level'],
                'STATE': 'C',
                'IS_DELETE': 0,
                'FULL_PATH': body['fullPath']
            }
            obj, created = Category.objects.update_or_create(CATEGORY_ID=body['categoryId'], defaults=item)
            if created:
                result = {
                    'code': 0,
                    'state': 1,
                    'data': body,
                    'msg': f'新建成功'
                }
            else:
                result = {
                    'code': 0,
                    'state': 0,
                    'data': body,
                    'msg': f'修改成功'
                }
            return JsonResponse(result)
        elif ptype == 'delete':
            body = json.loads(request.body)
            self.iter_delete(body['categoryId'])
            result = {
                'code': 0,
                'data': None,
                'msg': f'删除节点及其所有子孙节点成功'
            }
            return JsonResponse(result)


class SourceCRUD(APIView):
    """
    Method: GET
        type: list
        desc: 查询源的列表页数据
        url: http://localhost:8000/api/v1/source/source/list/?category_id=10121&page=3&limit=20
        return:
        ----------------------
        type: detail
        desc: 查询源的列表页数据
        url: http://localhost:8000/api/v1/source/source/detail/?category_id=10121&page=3&limit=20
        return:
        ----------------------
        type: queryCategory
        desc: 查询源对应的目录
        url: http://localhost:8000/api/v1/source/source/queryCategory/?sourceIds=6308234
        return:  {code: 0, data: [{}, {}...], msg: null}

    Method: POST
        type: addCategory
        desc: 查询源对应的目录
        url: http://localhost:8000/api/v1/source/source/addCategory/
        body: {
            'sourceIds': [1,2,3]
            'categoryId': xxx
        }
        return:  {code: 0, data: [{}, {}...], msg: null}
        ----------------------
        type: delCategory
        desc: 查询源对应的目录
        url: http://localhost:8000/api/v1/source/source/delCategory/
        body: {
            'sourceIds': [1,2,3]
            'categoryId': xxx
        }
        return:  {code: 0, data: [{}, {}...], msg: null}
        ----------------------
        type: addCategory
        desc: 查询源对应的目录
        url: http://localhost:8000/api/v1/source/source/modifyDetail/
        body: {
            ...
        }
        return:  {code: 0, data: [{}, {}...], msg: null}
        ----------------------

    """
    def __init__(self):
        super(SourceCRUD, self).__init__()
        self.logger = logging.getLogger('SourceCRUD')

    def get(self, request, **kwargs):
        ptype = kwargs['type']
        if ptype == 'list':
            category_ids = request.GET.get('category_id')
            page = int(request.GET['page'])
            limit = int(request.GET['limit'])
            offset = (page - 1) * limit
            if not category_ids:
                data = SourceBase.objects.filter(IS_DELETE=0).order_by('-SOURCE_ID')
                total = data.count()
                data = data[offset:offset + limit]
                data = [model_to_dict(_) for _ in data]
            else:
                items = Source2Category.objects.filter(CATEGORY_ID__in=category_ids.split(','))
                source_ids = [_.SOURCE_ID for _ in items]
                data = SourceBase.objects.filter(SOURCE_ID__in=source_ids, IS_DELETE=0).order_by('-SOURCE_ID')
                total = data.count()
                data = data[offset:offset + limit]
                data = [model_to_dict(_) for _ in data]
            result = {
                'code': 0,
                'num': len(data),
                'total': total,
                'data': data
            }
            return Response(result)
        elif ptype == 'detail':
            src_id = request.GET['src_id']
            if not src_id:
                src_id = -1
            data = SourceBase.objects.filter(SOURCE_ID=src_id).first()
            if data:
                result = {
                    'code': 0,
                    'data': model_to_dict(data),
                }
            else:
                result = {
                    'code': -1,
                    'data': '',
                    'msg': '源不存在',
                }
            return Response(result)
        elif ptype == 'queryCategory':
            ids = request.GET['sourceIds']
            sql = """
            select b.SOURCE_ID, b.SOURCE_NAME, c.CATEGORY_ID, c.CATEGORY_NAME, c.FULL_PATH from 
            source_2_category s2c JOIN
            source_category c JOIN
            source_base b
            WHERE c.CATEGORY_ID = s2c.CATEGORY_ID AND s2c.SOURCE_ID = b.SOURCE_ID
            AND s2c.SOURCE_ID in (%s)
            """ % ids
            query = Category.objects.raw(sql)
            data = [{
                'CATEGORY_ID': _.CATEGORY_ID,
                'CATEGORY_NAME': _.CATEGORY_NAME,
                'FULL_PATH': _.FULL_PATH,
                'SOURCE_ID': _.SOURCE_ID,
                'SOURCE_NAME': _.SOURCE_NAME
            } for _ in query]

            result = {
                'code': 0,
                'data': data,
                'msg': None
            }
            return Response(result)
        elif ptype == 'queryTimer':
            ids = request.GET['sourceIds']
            sql = """
            select b.SOURCE_NAME, s2t.SOURCE_ID, s2t.TIMER_ID, s2t.TIMER_TYPE, s2t.TIMER_EXP from 
            source_2_timer s2t JOIN
            source_base b
            WHERE s2t.SOURCE_ID = b.SOURCE_ID
            AND s2t.SOURCE_ID in (%s)
            """ % ids
            query = Source2Timer.objects.raw(sql)
            data = [{
                'sourceId': _.SOURCE_ID,
                'sourceName': _.SOURCE_NAME,
                'timerId': _.TIMER_ID,
                'timerType': _.TIMER_TYPE,
                'timerExp': _.TIMER_EXP
            } for _ in query]
            result = {
                'code': 0,
                'data': data,
                'msg': None
            }
            return Response(result)

    def post(self, request, **kwargs):
        ptype = kwargs['type']
        data = json.loads(request.body)
        if ptype == 'addCategory':
            sourceIds = data['sourceIds']
            categoryId = data['categoryId']
            exist = Category.objects.filter(CATEGORY_ID=categoryId, IS_DELETE=0).first()
            if not exist:
                result = {
                    'code': 100,
                    'data': None,
                    'create_num': None,
                    'msg': '目录ID不存在，请确认'
                }
                return Response(result)

            create_num = 0
            for src_id in sourceIds:
                if SourceBase.objects.filter(SOURCE_ID=src_id, IS_DELETE=0).all():
                    obj, created = Source2Category.objects.get_or_create(
                        SOURCE_ID=src_id,
                        CATEGORY_ID=categoryId,
                    )
                    if created:
                        create_num += 1
            result = {
                'code': 0,
                'data': None,
                'create_num': create_num,
                'msg': '新建成功'
            }
            return Response(result)
        if ptype == 'delCategory':
            sourceIds = data['sourceIds']
            categoryId = data['categoryId']
            exist = Category.objects.filter(CATEGORY_ID=categoryId, IS_DELETE=0).first()
            if not exist:
                result = {
                    'code': 100,
                    'data': None,
                    'create_num': None,
                    'msg': '目录ID不存在，请确认'
                }
                return Response(result)

            delete_num = 0
            for src_id in sourceIds:
                r = Source2Category.objects.filter(
                    SOURCE_ID=src_id,
                    CATEGORY_ID=categoryId,
                ).delete()
                delete_num += r[0]
            result = {
                'code': 0,
                'data': None,
                'delete_num': delete_num,
                'msg': '删除成功'
            }
            return Response(result)
        if ptype == 'modifyDetail':
            trans = {to_snake_case_upper(k): v for k, v in data.items()}
            SourceBase.objects.filter(SOURCE_ID=trans['SOURCE_ID']).update(**trans)
            result = {
                'code': 0,
                'msg': '修改成功'
            }
            return Response(result)
        if ptype == 'addTimer':
            checked_data = data['checkedData']
            freq = data['freq']
            for source_item in checked_data:
                task_id = str(uuid.uuid4())
                queue_params = {
                    "configId": str(source_item['CONFIG_ID']),
                    "configType": ConfigBase.objects.filter(CONFIG_ID=source_item['CONFIG_ID']).first().CONFIG_NAME,
                    "createTime": None,
                    "get_history": 0,
                    "max": None,
                    "message": None,
                    "min": None,
                    "param": {
                        "list": source_item['XPATH1'],
                        "detail": source_item['XPATH2'],
                        "other": source_item['SOURCE_PARAM'],
                    },
                    "parentId": "",
                    "priority": 50,
                    "retryCnt": 1,
                    "sendTime": None,
                    "sourceId": str(source_item['SOURCE_ID']),
                    "state": 0,
                    "tags": source_item['TAGS'],
                    "taskId": task_id,
                    "taskTitle": source_item['SOURCE_NAME'],
                    "timeout": 7200,
                    "url": source_item['SOURCE_URL']
                }
                params = {
                    'queue': ConfigBase.objects.filter(CONFIG_ID=source_item['CONFIG_ID']).first().SEND_TOPIC,
                    'queue_params': queue_params,
                }
                scheduler.add_job(
                    getattr(worker, 'rabbitmq_task'),
                    id=task_id,
                    trigger='interval',
                    seconds=int(freq),
                    kwargs=params,
                    misfire_grace_time=120
                )
                Source2Timer.objects.create(
                    SOURCE_ID=source_item['SOURCE_ID'],
                    TIMER_ID=task_id,
                    TIMER_TYPE='interval',
                    TIMER_EXP=freq,
                )
                self.logger.info(f'{source_item["SOURCE_ID"]} 添加定时任务成功，queue {params["queue"]} queue_params {queue_params} task_id  {task_id}')

            result = {
                'code': 0,
                'msg': f'添加{len(checked_data)}个定时任务成功',
                'data': ''
            }
            return Response(result)
        if ptype == 'delTimer':
            sourceIds = data['sourceIds']
            delete_num = 0
            for src_id in sourceIds:
                for timer in Source2Timer.objects.filter(SOURCE_ID=src_id).all():
                    scheduler.remove_job(
                        job_id=timer.TIMER_ID
                    )
                r = Source2Timer.objects.filter(
                    SOURCE_ID=src_id,
                ).delete()
                delete_num += r[0]
            result = {
                'code': 0,
                'data': None,
                'delete_num': delete_num,
                'msg': f'删除{delete_num}个定时任务成功'
            }
            return Response(result)
        if ptype == 'sendTask':     # 立即发送任务到队列中
            checked_data = data['checkedData']
            for source_item in checked_data:
                queue_params = {
                    "configId": str(source_item['CONFIG_ID']),
                    "configType": ConfigBase.objects.filter(CONFIG_ID=source_item['CONFIG_ID']).first().CONFIG_NAME,
                    "createTime": None,
                    "get_history": 0,
                    "max": None,
                    "message": None,
                    "min": None,
                    "param": {
                        "list": source_item['XPATH1'],
                        "detail": source_item['XPATH2'],
                        "other": source_item['SOURCE_PARAM'],
                    },
                    "parentId": "",
                    "priority": 50,
                    "retryCnt": 1,
                    "sendTime": None,
                    "sourceId": str(source_item['SOURCE_ID']),
                    "state": 0,
                    "tags": source_item['TAGS'],
                    "taskId": '',
                    "taskTitle": source_item['SOURCE_NAME'],
                    "timeout": 7200,
                    "url": source_item['SOURCE_URL']
                }
                params = {
                    'queue': ConfigBase.objects.filter(CONFIG_ID=source_item['CONFIG_ID']).first().SEND_TOPIC,
                    'queue_params': queue_params,
                }
                worker.rabbitmq_task(**params)
                self.logger.info(f'发送任务到 {params["queue"]} 成功')

            result = {
                'code': 0,
                'msg': f'发送 {len(checked_data)} 个任务成功',
                'data': ''
            }
            return Response(result)
        if ptype == 'addSource':
            print(data)
            detailData = data['detailData']
            source_items = detailData['data'].split('\n')
            for source in source_items:
                result = SourceBase.objects.all().aggregate(Max('SOURCE_ID'))
                if result['SOURCE_ID__max']:
                    source_id = result['SOURCE_ID__max'] + 1
                else:
                    source_id = 6000000

                source_name = source.split('$$$')[0].strip()
                source_url = source.split('$$$')[1].strip()
                obj, created = SourceBase.objects.get_or_create(
                    SOURCE_URL=source_url,
                    IS_DELETE=0,
                    defaults={
                        'SOURCE_ID': source_id,
                        'SOURCE_NAME': source_name,
                        'SOURCE_SITE': detailData['sourceSite'],
                        'CONFIG_ID': int(detailData['configId']),
                        'XPATH1': detailData['xpath1'],
                        'XPATH2': detailData['xpath2'],
                        'SOURCE_PARAM': detailData['sourceParam'],
                        'REMARK': detailData['remark'],
                        'DOMAIN': tldextract.extract(source_url).domain,
                        'STATE': detailData['state'],
                        'IS_DELETE': 0,
                    }
                )

                Source2Category.objects.get_or_create(SOURCE_ID=obj.SOURCE_ID, CATEGORY_ID=data['categoryId'])

            result = {
                'code': 0,
                'msg': f'添加 {len(source_items)} 个源成功',
                'data': ''
            }
            return Response(result)
        if ptype == 'delSource':
            ids = data['sourceIds']
            SourceBase.objects.filter(SOURCE_ID__in=ids).update(IS_DELETE=1)
            Source2Category.objects.filter(SOURCE_ID__in=ids).delete()
            result = {
                'code': 0,
                'data': None,
                'msg': f'删除{len(ids)}个源成功'
            }
            return Response(result)
        if ptype == 'copySource':
            target_ids = data['targetIds']
            source_id = data['sourceId']
            source = SourceBase.objects.filter(SOURCE_ID=source_id).first()
            SourceBase.objects.filter(SOURCE_ID__in=target_ids).update(
                CONFIG_ID=source.CONFIG_ID,
                XPATH1=source.XPATH1,
                XPATH2=source.XPATH2,
                SOURCE_PARAM=source.SOURCE_PARAM,
                STATE=source.STATE,
            )
            result = {
                'code': 0,
                'data': None,
                'msg': f'复制 {len(target_ids)} 个源配置成功'
            }
            return Response(result)


class SourceTopicCRUD(View):
    """
    http://localhost:8000/api/v1/source/topic/
    """

    def get(self, request):
        data = ConfigBase.objects.filter(IS_DELETE=0).all().values('CONFIG_ID', 'CONFIG_NAME')
        result = {
            'code': 0,
            'data': list(data),
        }
        return JsonResponse(result)


class SourceStateCRUD(View):
    """
    http://localhost:8000/api/v1/source/state
    """

    def get(self, request):
        data = SourceState.objects.all()
        result = {
            'code': 0,
            'data': [model_to_dict(_) for _ in data],
        }
        return JsonResponse(result)

    def post(self, request):
        data = eval(request.body.decode())
        obj, created = SourceState.objects.get_or_create(state=data['state'], remark=data['remark'])
        if created:
            result = {
                'code': 0,
                'msg': '创建成功',
            }
        else:
            result = {
                'code': 100,
                'msg': '状态已存在',
            }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

    def delete(self, request):
        data = eval(request.body.decode())
        deleted = SourceState.objects.filter(state=data['state']).delete()
        if deleted[0]:
            result = {
                'code': 0,
                'msg': '删除成功',
            }
        else:
            result = {
                'code': 100,
                'msg': '状态不存在',
            }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

    def put(self, request):
        data = eval(request.body.decode())
