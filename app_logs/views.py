import re
import time
import datetime
from django.http import HttpResponse, JsonResponse
from app_docs.models import Docs, DocsType
from django.http import HttpRequest
from elasticsearch import Elasticsearch
from crawler_studio_be.settings import ES_SERVER, ES_LOG_INDEX
from app_settings.models import LogServer


def search(request):
    """
    搜索日志
    http://localhost:8000/api/v1/logs/search/?addr=http:%2F%2F10.0.4.150:6800&job_id=c5c4107a633a11ec9f2d00163e290a0d&search=&dtrange_start=2021-12-25T18:36:57&dtrange_end=2021-12-25T18:46:57
    """
    dtrange_start = request.GET['dtrange_start'].replace('.000Z', '')
    dtrange_end = request.GET['dtrange_end'].replace('.000Z', '')
    addr = request.GET['addr']
    hostip = re.search(r'http://(.*):6800', addr).group(1)
    search = request.GET['search']
    job_id = request.GET['job_id']
    size = request.GET.get('size', 10000)
    # now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    # one_hour_ago = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
    # ten_minute = (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S')
    dsl = {
        "size": size,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "remote_ip.keyword": hostip
                        }
                    },
                    {
                        "regexp": {
                            "source": ".*{key}.*".format(key=job_id)
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gt": "{t}.000+0800".format(t=dtrange_start),
                                "lt": "{t}.000+0800".format(t=dtrange_end)
                            }
                        }
                    }
                ]
            }
        },
        "sort": {
            "@timestamp": {
                "order": "asc"
            }
        }
        # "aggs": {
        #     "log_level": {
        #         "terms": {
        #             "field": "log_level.keyword"
        #         },
        #         "aggs": {
        #             "source_count": {
        #                 "terms": {
        #                     "field": "source.keyword"
        #                 }
        #             }
        #         }
        #     }
        # }
    }
    print(dsl)
    es = Elasticsearch(hosts=f'http://{ES_SERVER}/')
    result = es.search(index=ES_LOG_INDEX, body=dsl)
    num = result['hits']['total']
    row_data = list()
    for hit in result['hits']['hits']:
        message = hit['_source']['message']
        # for key in message:
        #     server = LogServer.objects.filter(addr=key).first()
        #     if server:
        #         message[]
        # timestamp = hit['_source']['@timestamp']
        # d = parser.parse(timestamp)
        # d = d.astimezone(tz=pytz.timezone('Asia/Shanghai'))
        # timestamp = d.strftime('%Y-%m-%d %H:%M:%S')
        # parser.parse(timestamp)
        # module = hit['_source']['module']
        # log_level = hit['_source']['log_level']
        # row = f'{timestamp} [{module}] {log_level}: {message}'
        row_data.append(message)

    return JsonResponse({'code': 0, 'data': '\n'.join(row_data), 'num': num, 'size': size})


def analysis_spider_error_log_out(request: HttpRequest):
    """
    获取错误日志数据及比例

    """
    period = request.GET.get('period', 'all')
    addr = request.GET.get('addr')
    ip = addr.replace('http://', '').split(':')[0]

    if period == 'all':
        log_date_range = {
            "gte": "now-1y"
        }
    elif period == 'hour':
        log_date_range = {
            "gte": "now-1h"
        }
    else:
        log_date_range = {
            "gte": "now-1d"
        }

    es = Elasticsearch(['http://10.0.6.197', ], port=9200)
    today_log_result_by_spider = es.search(
        index=f'ocean_log',
        body={
            "size": 1,
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "remote_ip.keyword": ip
                            }
                        },
                        {
                            "range": {
                                "@timestamp": log_date_range
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "group_by_path": {
                    "terms": {
                        "field": "source.keyword",
                        "size": 1000
                    },
                    "aggs": {
                        "last_access": {
                            "max": {
                                "field": "@timestamp"
                            }
                        },
                        "count_error": {
                            "filter": {
                                "match": {
                                    "log_level.keyword": "ERROR"
                                }
                            }
                        }
                    }
                }
            }
        }
    )

    spider_error_info = list()
    for spider_file_error_info in today_log_result_by_spider['aggregations']['group_by_path']['buckets']:
        spider_name = spider_file_error_info['key'].split('/')[-2]
        spider_id = spider_file_error_info['key'].split('/')[-1].split('.')[0]
        last_log_time = spider_file_error_info['last_access']['value_as_string']
        seconds = int(time.time() - spider_file_error_info['last_access']['value'] // 1000)
        running_status = True if seconds <= 70 else False
        count = spider_file_error_info["doc_count"]
        error_count = spider_file_error_info['count_error']['doc_count']
        error_rate = error_count / count * 100
        spider_error_info.append(
            {
                'scrapyd': '',
                'spider_id': spider_id,
                'spider_name': spider_name,
                'last_log_time': last_log_time,
                'seconds': seconds,
                'running_status': running_status,
                'count': count,
                'error_count': error_count,
                'error_rate': error_rate,
            }
        )

    def take_seconds(elem):
        return elem['error_rate'] * (1 if elem['running_status'] else 0.001)

    spider_error_info.sort(key=take_seconds, reverse=True)
    return JsonResponse(
        {
            "status": "success" if all(i['error_count'] < 10 for i in spider_error_info) else 'failed',
            "total": len(spider_error_info),
            "records": spider_error_info
        }
    )


def group_error_log(request):
    """
    按时间和IP统计错误日志
    http://127.0.0.1:8000/api/v1/logs/group_error_log/?period=minute
    http://127.0.0.1:8000/api/v1/logs/group_error_log/?period=hour&day=today
    http://127.0.0.1:8000/api/v1/logs/group_error_log/?period=day
    """
    period = request.GET.get('period', 'all')
    if period == 'minute':
        log_date_range = {
            "gte": "{t}.000+0800".format(t=datetime.datetime.now().strftime('%Y-%m-%dT%H:00:00')),
        }
        group_time = {
            "field": "log_minute.keyword",
            "size": 70
        }
        log_time = f"{datetime.datetime.now().strftime('%Y-%m-%d %H')}:%s:00"
    elif period == 'hour':
        dtrange_start = request.GET['dtrange_start']
        dtrange_end = request.GET['dtrange_end']
        log_date_range = {
            "gt": "{t}.000+0800".format(t=dtrange_start),
            "lt": "{t}.000+0800".format(t=dtrange_end)
        }
        group_time = {
            "field": "log_hour.keyword",
            "size": 30
        }
        log_time = f"{datetime.datetime.now().strftime('%Y-%m-%d')} %s:00:00"
    else:
        log_date_range = {
            "gte": "now-1w"
        }
        group_time = {
            "script": "doc['log_date'].value.dayOfMonth",
            "size": 50
        }
        log_time = f"{datetime.datetime.now().strftime('%Y-%m')}-%s 00:00:00"

    dsl = {
        "size": 1,
        "query": {
          "bool": {
            "must": [
              {
                "term": {
                  "log_level.keyword": "ERROR"
                }
              },
              {
                "range": {
                  "@timestamp": log_date_range
                }
              }
            ]
          }
        },
        "aggs": {
          "group_by_time": {
            "terms": group_time,
            "aggs": {
              "group_by_ip": {
                "terms": {
                  "field": "remote_ip.keyword"
                }
              }
            }
          }
        }
    }
    es = Elasticsearch(hosts=f'http://{ES_SERVER}/')
    result = es.search(index=ES_LOG_INDEX, body=dsl)
    num = result['hits']['total']
    data = list()
    exist_ip = {log['key'] for t in result['aggregations']['group_by_time']['buckets'] for log in t['group_by_ip']['buckets']}
    for time_bucket in result['aggregations']['group_by_time']['buckets']:
        row_data = dict()
        from dateutil import parser as dtparser
        row_data['时间'] = dtparser.parse(log_time % time_bucket['key'])
        ip_count_pair = {_['key']: _['doc_count'] for _ in time_bucket['group_by_ip']['buckets']}
        for ip in exist_ip:
            if ip not in ip_count_pair:
                row_data[ip] = 0
            else:
                row_data[ip] = ip_count_pair[ip]
        data.append(row_data)
    data.sort(key=lambda _: _['时间'], reverse=False)
    return JsonResponse({
        'code': 0,
        'data': data,
        'num': num
    })
