import re
import time
import logging
import datetime
from rest_framework.views import APIView
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
        date = request.query_params['date']
        today = datetime.datetime.now().date()
        weekday = datetime.datetime.now().weekday()
        tomorrow = today + datetime.timedelta(1)
        yestoday = today - datetime.timedelta(1)
        before_yestoday = today - datetime.timedelta(2)
        week_start = today - datetime.timedelta(days=weekday)
        if date == 'today':
            date_range = [today, tomorrow]
        elif date == 'yestoday':
            date_range = [yestoday, today]
        elif date == 'before_yestoday':
            date_range = [before_yestoday, yestoday]
        else:
            date_range = [week_start, tomorrow]

        queryset = ErrorLog.objects.filter(
            host=request.query_params['host'],
            project__icontains=request.query_params['project'],
            spider__contains=request.query_params['spider'],
            job_id__icontains=request.query_params['jobId'],
            content__icontains=request.query_params['content'],
            create_time__range=date_range
        ).order_by('-record_time')
        page_obj = self.PageNumberPagination()
        page_data = page_obj.paginate_queryset(queryset, request)
        ser = ErrorLogSer(page_data, many=True)

        page_size = page_obj.get_page_size(request)
        paginator = page_obj.django_paginator_class(queryset, page_size)
        page_number = page_obj.get_page_number(request, paginator)
        res = {
            'code': 200,
            'data': {
                'data': ser.data,
                'total': queryset.count(),
                'page': int(page_number),
                'pageSize': page_size
            },
            'message': 'ok'
        }
        return Response(res)

    def post(self, request, **kwargs):
        data = ErrorLogSer(data=request.data, many=True)
        if data.is_valid():
            data.save()
            return Response(f'create success({len(request.data)})', status=status.HTTP_200_OK)
        else:
            self.logger.error(data.errors)
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)


class ErrorLogGroupFromSql(APIView):

    def post(self, request, **kwargs):
        request_data = request.data
        date = request_data['date']
        if date == 'today':
            date_range = 'log_date = DATE()'
        elif date == 'yestoday':
            date_range = 'log_date = DATE()-1'
        elif date == 'before_yestoday':
            date_range = 'log_date = DATE()-2'
        else:
            date_range = "DATE(log_date) >= DATE('now', 'weekday 0', '-7 days')"

        server = request_data["server"] or [""]
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
            {} and host in ({})
        GROUP BY
            host,
            log_hour;
        """.format(date_range, ','.join(repr(_) for _ in server))
        print(sql)
        result = HourlyErrLogRate.objects.raw(sql)
        hosts = set(_.host for _ in result)
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        now_hour = datetime.datetime.now().hour
        timeline = []
        series = dict()
        for hour in range(now_hour+1):
            timeline.append(f'{str(hour).zfill(2)}')
            for host in hosts:
                if host not in series:
                    series[host] = []

                hour_exist = False
                for item in result:
                    if item.host == host and int(item.log_hour) == hour:
                        series[host].append(int(item.err_count))
                        hour_exist = True

                if not hour_exist:
                    series[host].append(0)

        res = {
            'code': 200,
            'data': {
                'data': {
                    'xAxis': timeline if series else [],
                    'series': series
                }
            },
            'message': 'ok'
        }
        return Response(res)


class HostErrorLogGroupFromSql(APIView):

    def post(self, request, **kwargs):
        request_data = request.data
        date = request_data['date']
        if date == 'today':
            date_range = 'log_date = DATE()'
        elif date == 'yestoday':
            date_range = 'log_date = DATE()-1'
        elif date == 'before_yestoday':
            date_range = 'log_date = DATE()-2'
        else:
            date_range = "DATE(log_date) >= DATE('now', 'weekday 0', '-7 days')"

        server = request_data["server"] or [""]
        sql = """
        SELECT 
            id,
            host,
            project,
            spider,
            log_date,
            sum( log_error_count ) as err_count
        FROM
            app_logs_dailyerrlograte
        WHERE
            {} and host in ({})
        GROUP BY
            host,
            spider
        ORDER BY
            err_count desc
        """.format(date_range, ','.join(repr(_) for _ in server))
        print(sql)
        result = DailyErrLogRate.objects.raw(sql)
        spiders = list(_.spider for _ in result)[:5]
        error_log_count = list(int(_.err_count) for _ in result)[:5]
        res = {
            'code': 200,
            'data': {
                'data': {
                    'xAxis': spiders,
                    'series': error_log_count
                }
            },
            'message': 'ok'
        }
        return Response(res)
