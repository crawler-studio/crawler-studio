import re
import time
import logging
import datetime
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from .models import HourlyErrLogRate, DailyErrLogRate, ErrorLog
from .ser import HourlyErrLogRateSer, DailyErrLogRateSer, ErrorLogSer
from rest_framework import status, pagination


class ErrorLogRateCRUD(APIView):

    def __init__(self):
        super(ErrorLogRateCRUD, self).__init__()
        self.logger = logging.getLogger('ErrorLogRateCRUD')

    def get(self, request, **kwargs):
        pass

    def post(self, request, **kwargs):
        if request.data.get('log_hour') is not None:        # hourly api
            job_id = request.data['job_id']
            log_date = request.data['log_date']
            log_hour = request.data['log_hour']
            existed = HourlyErrLogRate.objects.filter(job_id=job_id, log_date=log_date, log_hour=log_hour).first()
            data = HourlyErrLogRateSer(instance=existed, data=request.data)
            if data.is_valid():
                data.save()
                if existed:
                    return Response(f'update success {job_id} {log_date}-{log_hour}', status=status.HTTP_200_OK)
                else:
                    return Response(f'create success {job_id} {log_date}-{log_hour}', status=status.HTTP_200_OK)
            else:
                self.logger.error(data.errors)
                return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            job_id = request.data['job_id']             # daily api
            log_date = request.data['log_date']
            existed = DailyErrLogRate.objects.filter(job_id=job_id, log_date=log_date).first()
            data = DailyErrLogRateSer(instance=existed, data=request.data)
            if data.is_valid():
                data.save()
                if existed:
                    return Response(f'update success {job_id} {log_date}', status=status.HTTP_200_OK)
                else:
                    return Response(f'create success {job_id} {log_date}', status=status.HTTP_200_OK)
            else:
                self.logger.error(data.errors)
                return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)                # daily api


class ErrorLogContentCRUD(APIView):

    class PageNumberPagination(pagination.PageNumberPagination):
        """查第n页，每页显示n条数据"""
        page_size = 50  # 指定每页显示多少条数据
        page_size_query_param = 'pageSize'
        page_query_param = 'page'
        max_page_size = None

    def __init__(self):
        super(ErrorLogContentCRUD, self).__init__()
        self.logger = logging.getLogger('ErrorLogContentCRUD')

    def get(self, request, **kwargs):
        queryset = ErrorLog.objects.filter(
            project__icontains=request.query_params['project'],
            spider__contains=request.query_params['spider'],
            job_id__icontains=request.query_params['jobId'],
            content__icontains=request.query_params['content']
        ).order_by('-record_time')
        page_obj = self.PageNumberPagination()
        page_data = page_obj.paginate_queryset(queryset, request)
        ser = ErrorLogSer(page_data, many=True)

        page_size = page_obj.get_page_size(request)
        paginator = page_obj.django_paginator_class(queryset, page_size)
        page_number = page_obj.get_page_number(request, paginator)

        return Response({
            'code': 200,
            'data': {
                'data': ser.data,
                'total': queryset.count(),
                'page': int(page_number),
                'pageSize': page_size
            },
            'message': 'ok'
        })

    def post(self, request, **kwargs):
        data = ErrorLogSer(data=request.data, many=True)
        if data.is_valid():
            data.save()
            return Response(f'create success', status=status.HTTP_200_OK)
        else:
            self.logger.error(data.errors)
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)


def error_log_group_from_sql(request):
    sql = """
    SELECT 
        id,
        host,
        log_hour,
        log_date,
        sum( log_error_count ) as err_count
    FROM
        app_logs_hourlyerrlograte 
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

