import re
import time
import datetime
from django.http import HttpResponse, JsonResponse
from crawler_studio.app_scrapyd.models import HourlyErrLogRate, ErrorLog
from rest_framework.decorators import api_view
from rest_framework.response import Response


def error_log_group_from_sql(request):
    sql = """
    SELECT 
        id,
        host,
        log_hour,
        log_date,
        sum( log_error_count ) as err_count
    FROM
        app_scrapyd_hourlyerrlograte 
    WHERE
        log_date = CURDATE()
    GROUP BY
        host,
        log_hour;
    """
    result = HourlyErrLogRate.objects.raw(sql)
    hosts = set(_.host for _ in result)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    now_hour = datetime.datetime.now().hour
    data = []
    for hour in range(now_hour+1):
        row_data = dict()
        row_data['时间'] = f'{today}T{str(hour).zfill(2)}:00:00'
        for host in hosts:
            for item in result:
                if item.host == host and item.log_hour == hour:
                    row_data[host] = item.err_count

            if host not in row_data:
                row_data[host] = 0
        data.append(row_data)

    data.sort(key=lambda _: _['时间'], reverse=False)
    return JsonResponse({
        'code': 200,
        'data': {
            'data': data
        },
        'message': 'ok'
    })

